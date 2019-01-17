import numpy as np


class LCS:

    def __init__(self, relation):
        self.relation = relation

    def lcs_sim(self, s1, s2):
        dp = np.zeros((len(s1)+1, len(s2)+1))
        for i in range(len(s1)):
            for j in range(len(s2)):
                if s1[i] == s2[j]:
                    dp[i+1][j+1] = dp[i][j] + 1
                else:
                    dp[i+1][j+1] = max(dp[i][j+1], dp[i+1][j])
        return dp[-1][-1]

    def predict(self, s):
        sims = [self.lcs_sim(r, s) for r in self.relation]
        emotion = sims.index(max(sims))
        if len(s) <= 2:
            return -1
        else:
            return emotion

relation = np.loadtxt('EmoReco.txt')
lcs = LCS(relation)
