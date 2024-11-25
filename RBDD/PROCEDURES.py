class PROCEDURES:

    @staticmethod
    def entails(rbdd, cbdd):
        ranks = [set() for i in range(0, len(rbdd.ranks))]

        def applý_step(v1, v2):
            if v1.val == -1 or v2.val == -1:
                return
            if v1.val == "X" and v2.val == "X":
                index = min(v1.index,v2.index)
                if v1.index == index:
                    vleft1 = v1.left
                    vright1 = v1.right
                else:
                    vleft1 = v1
                    vright1 = v1
                if v2.index == index:
                    vleft2 = v2.left
                    vright2 = v2.right
                else:
                    vleft2 = v2
                    vright2 = v2
                applý_step(vleft1, vleft2)
                applý_step(vright1, vright2)
                return
            elif v1.val != "X":
                v2_ranks = v2.ranks
                ranks[v1.val] = ranks[v1.val] | v2_ranks
                return
            elif v2.val != "X":
                v1_ranks = v1.ranks
                v2_ranks = v2.ranks
                for rank in v1_ranks:
                    if rank != -1:
                        ranks[rank] = ranks[rank] | v2_ranks
                return
        
        applý_step(rbdd, cbdd)
        for rank_set in ranks:
            if 1 in rank_set:
                return False
            if 0 in rank_set:
                return True
        return False
        