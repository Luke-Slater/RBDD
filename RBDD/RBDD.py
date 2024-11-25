from pysat.formula import *
import copy, time, re

class Node:
    def __init__(self, id=None, index=None, val=None, mark=False, left=None, right=None):
        self.id = id
        self.index = index
        self.val = val
        self.mark = mark
        self.left = left
        self.right = right
        self.ranks = None

    def find_ranks(self, set):
        if self.val != "X":
            set = set | {self.val}
            self.ranks = set
        else:
            set_left = self.left.find_ranks(set)
            set_right = self.right.find_ranks(set)
            set = set | set_left | set_right
            self.ranks = set

    def write_to_file(self, name):
        self.mark = not self.mark
        if self.left is None:
            left_id = -1
        else:
            left_id = self.left.id
            if self.mark ^ self.left.mark: self.left.write_to_file(name)
        if self.right is None:
            right_id = -1
        else:
            right_id = self.right.id
            if self.mark ^ self.right.mark: self.right.write_to_file(name)

        with open(name, 'a') as file:
            line = f"{self.id} {self.index} {self.val} {left_id} {right_id}\n"
            file.write(line)

class RBDD:

    max_rank = 0
    num_nodes = 0

    @staticmethod
    def from_file(file):
        with open(file, 'r') as file:
            content = file.readlines()
        content = content[3:]
        nodes = [Node() for i in range(0, len(content))]
        for line in content:
            data = line.split(" ")
            id = int(data[0])
            index = int(data[1])
            val = data[2]
            left = int(data[3])
            right = int(data[4])
            nodes[id] = Node(id=id, index=index, val=val, left=left, right=right)
        for node in nodes:
            if node.left != -1:
                node.left = nodes[node.left]
            if node.right != -1:
                node.right = nodes[node.right]
        for node in nodes:
            if node.index == 1:
                node.find_ranks(set())
                return node

    @staticmethod
    def build_sysz(K, ordering):
        global max_rank
        global num_nodes

        max_rank = len(K)-1
        num_nodes = 0

        def build_step(K, ass, ordering):
            global max_rank
            global num_nodes

            def process_node(K, ass):
                global max_rank
                global num_nodes

                K = [k.simplified(assumptions=ass) if (k!=Atom(True))and(k!=Atom(False)) else k for k in K]
                #r = [k.satisfied(model=ass) for k in K]

                for i in range(0, len(K)):
                    if K[i] != Atom(True) and K[i] != Atom(False):
                        return "CONT", -1, K
                    elif K[i] == Atom(False) and i == len(K)-1:
                        return "INF", -1, K
                    elif K[i] == Atom(False):
                        if K[i+1] == Atom(True):
                            return "RANK", i+1, K
                    elif K[i] == Atom(True):
                        return "RANK", i, K
                    else:
                        return "CONT", -1, K


            num_nodes += 1
            node = Node(id=num_nodes)
            res, ran, K = process_node(K, ass)
            if res == "INF":
                node.val = -1
                node.index = len(ordering)
                return node
            elif res == "RANK":
                node.val = ran
                node.index = len(ordering)
                return node
            elif res == "CONT":
                node.val = "X"
                index = len(ass) + 1

                v = ordering[index]
                while True:
                    pattern = r'\b' + re.escape(str(v)) + r'\b'
                    contains = [re.search(pattern, str(formula)) for formula in K]
                    if not any(contains):
                        index += 1
                        v = ordering[index]
                    else:
                        break   
                v = Atom(v)
                node.index = index
                node.left = build_step(K, ass + [~v], ordering)
                node.right = build_step(K, ass + [v], ordering)
                return node
        node = Node(id=0, index=1, val="X")
        node.left = build_step(K, [~Atom(ordering[1])], ordering)
        node.right = build_step(K, [Atom(ordering[1])], ordering)
        return RBDD.reducè(node, ordering, num_nodes)

    @staticmethod
    def reducè(node, ordering, num_nodes):
        subgraph = [Node() for i in range(0, num_nodes+1)]
        vlist = [[] for i in range(0, len(ordering)+1)]
        vlist = RBDD.traverse(node, RBDD.popVlist, vlist)
        nextid = 0
        for i in range(len(ordering), 0, -1):
            Q = []
            for u in vlist[i]:
                if u.index == len(ordering):
                    Q.append(((u.val,), u))
                elif u.left.id == u.right.id:
                    u.id = u.left.id
                else:
                    Q.append(((u.left.id, u.right.id), u)) 
            Q = sorted(Q, key=lambda x: (x[0][0], x[0][1] if len(x[0]) > 1 else float('-inf')))
            oldkey = (-2,-2)
            for (key,u) in Q:
                if key == oldkey:
                    u.id = nextid
                else:
                    nextid += 1
                    u.id = nextid
                    subgraph[nextid] = u
                    if u.index != len(ordering):
                        u.left = subgraph[u.left.id]
                        u.right = subgraph[u.right.id]
                    oldkey = key
        return subgraph[node.id], int(RBDD.traverse(subgraph[node.id],RBDD.countNodes,[0])[0])
    
    @staticmethod
    def traverse(node, function, list):
        def traverse_step(node, function, list):
            node.mark = not node.mark
            list = function(node, list)
            if node.val == "X":
                if node.mark ^ node.left.mark: list = traverse_step(node.left, function, list)
                if node.mark ^ node.right.mark: list = traverse_step(node.right, function, list)
            return list
        return traverse_step(node, function, list)
    
    @staticmethod
    def popVlist(node, list):
        list[node.index].append(node)
        return list
    
    @staticmethod
    def popNodeString(node, text):
        if node._0 is None:
            left = -1
        else: left = node._0.id
        if node._1 is None:
            right = -1
        else: right = node._1.id
        if not isinstance(node.value, int):
            value = -2
        else: value = node.value
        text[0] = text[0] + str(node.id) + " " + str(node.index) + " " + str(left) + " " + str(right) + " " + str(value) + "\n"
        return text
    
    @staticmethod
    def countNodes(_, list):
        list[0] += 1
        return list
    
    