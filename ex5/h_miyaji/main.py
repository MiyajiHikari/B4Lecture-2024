"""This module performs a fitting of the data using the EM algorithm."""

import argparse

import matplotlib.pyplot as plt
import numpy as np

import ex3


# TODO:　後で変える
def parse_args():
    """Retrieve variables from the command prompt."""
    parser = argparse.ArgumentParser(description="performs a fitting of tha data.")

    # csv file name
    parser.add_argument("--input-file", type=str, required=True, help="input csv file")

    # number of clusters for Gaussian distribution
    parser.add_argument("--cluster-num", type=int, default=1, help="number of clusters")

    return parser.parse_args()


# θ初期化する関数(-> means, cov_matrix, weights)が欲しいかも
def initialize_gmm(
    dataset: np.ndarray, cluster_num: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Initialize the means, covariance matrix and weights.

    Args:
        dataset (np.ndarray): csv data (n, dim).
        cluster_num (int): number of clusters.

    Returns:
        means (np.ndarray): mean for each cluster (k, dim).
        cov_matrix (np.ndarray): covariance matrix for each cluster (k, dim, dim).
        weights (np.ndarray): weight of each Gaussian (k, ).
    """
    # dimension of the data
    if isinstance(dataset[0], np.ndarray):
        dim = len(dataset[0])
    else:
        dim = 1

    means = np.random.randn(cluster_num, dim)  # (k, dim)
    cov_matrix = np.array([np.eye(dim) for k in range(cluster_num)])  # (k, dim, dim)
    weights = np.array([1 / cluster_num for k in range(cluster_num)])  # (k, )
    return means, cov_matrix, weights


# TODO:　一旦目をつぶる（後でやる）　分散共分散行列を計算するやつ　初期化を単位行列にするなら要らんかも
def calc_cov_matrix(dataset: np.ndarray, means: np.ndarray) -> np.ndarray:
    """Calculate covariance matrix.

    Args:
        dataset (np.ndarray): csv data.
        means (np.ndarray): mean vector (dim(dataset),)

    Returns:
        np.ndarray: _description_
    """
    # dimension of the data
    if isinstance(dataset[0], np.ndarray):
        dim = len(dataset[0])
    else:
        dim = 1

    num = len(dataset)  # number of the data

    # calculate mean of x and x^2
    mean = np.zeros(dataset.shape)
    mean_xx = np.zeros(dataset.shape)
    for i in range(dim):
        mean[:, i] += sum(dataset[:, i]) / num
        mean_xx[:, i] += sum(dataset[:, i] ** 2) / num

    # standardization = sqrt(mean(x^2) - mean(x)^2)
    sd = (mean_xx - (mean**2)) ** 0.5
    sd_data = (dataset - mean) / sd

    # calculate covariance matrix
    cov_matrix = np.zeros((dim, dim))
    var_matrix = np.zeros((dim, dim))

    for i in range(dim):  # variance (σ^2)
        var_matrix[i, i] = sum((dataset[:, i] - means[:, i]) ** 2)
        for j in range(i + 1, dim):  # upper triangular matrix
            cov_matrix[i, j] = sum((dataset[:, i] * dataset[:, j]))
    # symmetric matrix
    cov_matrix = (cov_matrix + cov_matrix.T + var_matrix) / num
    return cov_matrix


# 多変量ガウス関数を計算するやつ　入力するxは１個のデータ点とする -> float
def get_gauss(data: np.ndarray, mean: np.ndarray, cov_matrix: np.ndarray) -> float:
    """Get the value of the Gaussian distribution.

    Args:
        data (np.ndarray): one of the csv data (dim,).
        mean (np.ndarray): mean in one cluster (dim,).
        cov_matrix (np.ndarray): covariance matrix in one cluster (dim, dim).

    Returns:
        gauss (float): the value of the Gaussian distribution.
    """
    # dimension of the data
    if type(data) is np.ndarray:
        dim = len(data)
    else:
        dim = 1

    gauss_denominator = (np.sqrt(2 * np.pi) ** dim) * np.sqrt(np.linalg.det(cov_matrix))

    # TODO: dataとmeanを縦ベクトルにしないといけない可能性がある　実行してみて次元エラーが出たら.Tの位置を逆にしてみる
    gauss_numerator = np.exp(
        ((data - mean) @ np.linalg.inv(cov_matrix) @ (data - mean)[:, np.newaxis]) / -2
    )
    gauss = gauss_numerator / gauss_denominator
    return gauss


# 混合ガウス分布の値を計算する　Xはcsvデータ全体、返す値も全体にする（各ガウス分布の値を残しておく） ->(k, n)
def calc_mix_gauss(
    dataset: np.ndarray,
    means: np.ndarray,
    cov_matrix: np.ndarray,
    weights: np.ndarray,
) -> np.ndarray:
    """Calculate values of mix Gaussian distribution.

    Args:
        dataset (np.ndarray): csv data (n, dim).
        means (np.ndarray): mean for each cluster (k, dim).
        cov_matrix (np.ndarray): covariance matrix for each cluster (k, dim, dim).
        weights (np.ndarray): weight of each Gaussian (k, ).

    Returns:
        mix_gauss (np.ndarray): values of mix Gaussian distribution (k, n).
    """
    cluster_num = len(weights)  # number of Gaussian
    data_num = len(dataset)  # number of data (csv plot)

    mix_gauss = np.zeros((cluster_num, data_num))
    # TODO: お前を消す方法
    for k in range(cluster_num):
        for n in range(data_num):
            mix_gauss[k, n] = weights[k] * get_gauss(
                dataset[n], means[k], cov_matrix[k]
            )
    return mix_gauss


# EMアルゴリズムで新しいθ = {μ, Σ, π}を求める
def em_algo(
    dataset: np.ndarray,
    means: np.ndarray,
    cov_matrix: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Update parameters with EM algorithm.

    Args:
        dataset (np.ndarray): csv data (n, dim).
        means (np.ndarray): mean for each cluster (k, dim).
        cov_matrix (np.ndarray): covariance matrix for each cluster (k, dim, dim).
        weights (np.ndarray): weight of each Gaussian (k, ).

    Returns:
        new_means (np.ndarray): updated means (k, dim).
        new_cov_matrix(np.ndarray): updated cov_matrix (k, dim, dim).
        new_weights (np.ndarray): updated weights (k, ).
    """
    cluster_num = len(weights)  # number of Gaussian
    data_num = len(dataset)  # number of data (csv plot)
    if isinstance(dataset[0], np.ndarray):
        dim = len(dataset[0])  # dimension of the data
    else:
        dim = 1
        dataset = dataset[:, np.newaxis]

    # E step : calculate burden ratio
    mix_gauss = calc_mix_gauss(dataset, means, cov_matrix, weights)
    burden_ratio = (
        mix_gauss.T / np.sum(mix_gauss, axis=0)[:, np.newaxis]
    )  # gamma (n, k)

    # M step : update θ = {π, μ, Σ}
    N_k = np.sum(burden_ratio, axis=0)  # (k, )
    N = np.sum(N_k)  # N = data_num (float)
    new_weights = N_k / N

    new_means = np.zeros((cluster_num, dim))
    for k in range(cluster_num):
        # sum( (1, dim)*(n, dim), axis=0 ) = sum( (n, dim), axis=0 ) = (dim, )
        new_means[k, :] = (
            np.sum(burden_ratio[:, k][:, np.newaxis] * dataset, axis=0) / N_k[k]
        )

    new_cov_matrix = np.zeros((cluster_num, dim, dim))
    deviation = (
        dataset[np.newaxis, :, :] - new_means[:, np.newaxis, :]
    )  # x(1, n, dim) - μ(k, 1, dim) = (k, n, dim)
    # TODO: 二重forに敗北した
    for k in range(cluster_num):
        for n in range(data_num):
            tmp = deviation[k, n, :][:, np.newaxis] @ deviation[k, n, :][np.newaxis, :]
            new_cov_matrix[k, :, :] += burden_ratio[n, k] * tmp
        new_cov_matrix[k, :, :] /= N_k[k]

    return new_means, new_cov_matrix, new_weights


# 対数尤度関数の値(float)を返す
def get_log_likelihood(
    dataset: np.ndarray,
    means: np.ndarray,
    cov_matrix: np.ndarray,
    weights: np.ndarray,
) -> float:
    """get the value of log-likelihood.

    Args:
        dataset (np.ndarray): csv data (n, dim).
        means (np.ndarray): mean for each cluster (k, dim).
        cov_matrix (np.ndarray): covariance matrix for each cluster (k, dim, dim).
        weights (np.ndarray): weight of each Gaussian (k, ).

    Returns:
        log_likelihood (float): the value of log-likelihood.
    """
    log_likelihood = np.sum(
        np.log(np.sum(calc_mix_gauss(dataset, means, cov_matrix, weights), axis=0))
    )
    return log_likelihood


# ----以下ex4----


def plot_bases(trans_matrix: np.ndarray, ax, cont: np.ndarray):
    """Plot the bases on a scatter plot.

    Args:
        trans_matrix (np.ndarray): transformation matrix.
        ax (Axis): Axis object of the scatter plot.
        cont (np.ndarray): contribution rates.

    Returns:
        ax: Axis object of the graph.
    """
    dim = len(trans_matrix[0])  # dimension of the data after transformation
    colors = ("b", "g", "r")  # color of line (blue, green, red)

    if dim == 2:  # x-y
        for i in range(dim):
            eig_vec = trans_matrix[:, i]
            cr = cont[i]  # contribution rate
            ax.axline(
                [0, 0], eig_vec, label=f"Contribution rate: {cr:3.3f}", color=colors[i]
            )

    elif dim == 3:  # x-y-z
        for i in range(dim):
            eig_vec = trans_matrix[:, i]
            cr = cont[i]  # contribution rate

            t = np.array([-2.5, 2.5])  # range of line
            line_points = t[:, np.newaxis] * eig_vec

            ax.plot(
                line_points[:, 0],
                line_points[:, 1],
                line_points[:, 2],
                label=f"Contribution rate: {cr:3.3f}",
                color=colors[i],
            )

    ax.legend()
    # plt.savefig("h_miyaji\\figs\\result2-1.png")
    plt.show()
    return ax


def main():
    """Load csv file and a fitting of the data using the EM algorithm."""
    # get argument
    args = parse_args()
    filename = args.input_file  # csv file name
    cluster_num = args.cluster_num  # number of clusters for Gaussian distribution

    # load csv file
    data = ex3.load_data(filename)

    # dimension of the data
    if type(data[0]) is np.ndarray:
        dim = len(data[0])
    else:
        dim = 1

    # plot csv data (2d or 3d)
    if dim <= 3:
        ax = ex3.plot_scatter_diag(data, title=filename[2:-4])
        plt.show()

    # initialize gmm parameters
    means, cov_matrix, weights = initialize_gmm(data, cluster_num)

    print("----------- old log likelihood -----------")

    # calculate log-likelihood
    ll_old = get_log_likelihood(data, means, cov_matrix, weights)
    print(f"{ll_old=}\n{means=}\n{cov_matrix=}\n{weights=}")  # TODO: print

    print("----------- em algo -----------")
    # EM algorithm
    new_means, new_cov_matrix, new_weights = em_algo(data, means, cov_matrix, weights)

    print("----------- new log likelihood -----------")
    ll_new = get_log_likelihood(data, new_means, new_cov_matrix, new_weights)
    print(f"{ll_new=}\n{new_means=}\n{new_cov_matrix=}\n{new_weights=}")  # TODO: print

    # ----以下ex4----

    # # plot base lines (2d or 3d)
    # if dim <= 3:
    #     plot_bases(trans_matrix, ax, cont)

    # # dimensionality reduction (3d -> 2d)
    # if dim == 3:
    #     trans_data = (trans_matrix.T @ data.T).T  # y_i = A.T @ x_i
    #     data_2d = trans_data[:, :-1]  # 3d -> 2d
    #     ex3.plot_scatter_diag(
    #         data_2d, "After Dimensionality Reduction", xlabel="PC1", ylabel="PC2"
    #     )
    #     # plt.savefig("h_miyaji\\figs\\result2-2.png")
    #     plt.show()


if __name__ == "__main__":
    main()