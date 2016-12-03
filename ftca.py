import numpy as np
from copy import deepcopy


class FTCA():

    def __init__(self, threshold, period, verbose=None):
        self.threshold = threshold
        self.period = period
        self.verbose = verbose
        self.assets_prices = None
        self.corr_matrix_orig = None
        self.clusters = {}

    def calc_corr_matrix(self):
        """
        Calculates the correlation matrix based on the return
        (as given by period. e.g: 1 => daily return)
        :return: A n_assets X n_assets matrix
        """
        period_return = self.assets_prices.pct_change(self.period).iloc[1:]
        corr_matrix = period_return.corr()
        corr_matrix[corr_matrix == 1.0] = np.nan
        return corr_matrix

    @staticmethod
    def remove_asset_from_corr_matrix(mat, assets):
        mat.drop(assets, axis=1, inplace=True)  # Drop row
        mat.drop(assets, axis=0, inplace=True)  # Drop column
        return mat

    def add_new_cluster(self):
        if not self.clusters:
            self.clusters[1] = None
        else:
            self.clusters[max(self.clusters) + 1] = None
        if self.verbose:
            print 'Created new cluster number %d' % len(self.clusters)

    def set_new_cluster(self, curr_assets_to_add, curr_corr_matrix):
        self.add_new_cluster()
        self.clusters[max(self.clusters)] = curr_assets_to_add
        curr_corr_matrix = self.remove_asset_from_corr_matrix(
            curr_corr_matrix, curr_assets_to_add)
        return curr_corr_matrix

    def apply_ftca(self, assets_prices):
        self.assets_prices = assets_prices
        self.corr_matrix_orig = self.calc_corr_matrix()
        corr_matrix = deepcopy(self.corr_matrix_orig)

        while corr_matrix.shape != (0, 0):
            if self.verbose:
                print 'Current corr matrix shape: %s' % (corr_matrix.shape, )
            if corr_matrix.shape == (1, 1):
                corr_matrix = self.set_new_cluster(corr_matrix.index.tolist(),
                                                   corr_matrix)
            else:
                hc = corr_matrix.mean(1).argmax()
                lc = corr_matrix.mean(1).argmin()
                if corr_matrix.loc[hc, lc] > self.threshold:
                    assets_to_add = list(
                        set([lc, hc] + corr_matrix[
                            corr_matrix[[lc, hc]].mean(
                                1) > self.threshold].index.tolist()))
                    corr_matrix = self.set_new_cluster(assets_to_add,
                                                       corr_matrix)
                else:
                    if corr_matrix.shape == (2, 2):
                        for asset in corr_matrix.index.tolist():
                            corr_matrix = self.set_new_cluster([asset],
                                                               corr_matrix)
                    else:
                        for asset in [lc, hc]:
                            assets_to_add = list(
                                set([asset] +
                                    corr_matrix[corr_matrix[
                                                    asset] > self.threshold].index.tolist()))
                            corr_matrix = self.set_new_cluster(assets_to_add,
                                                               corr_matrix)
        self.clusters = {'Cluster_' + str(k): v for k, v in
                         self.clusters.iteritems()}
