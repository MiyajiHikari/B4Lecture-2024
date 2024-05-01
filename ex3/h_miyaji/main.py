"""最小二乗法を用いて回帰分析を行う."""

import matplotlib.pyplot as plt  # グラフ描画
import numpy as np  # 線形代数
from mpl_toolkits.mplot3d import Axes3D


def load_data(filename: str) -> np.ndarray:
    """csvファイルからndarray配列を作成.

    Args:
        filename (str): csvファイルの名前

    Returns:
        np.ndarray: csvファイル内のデータ
    """
    data_set = np.loadtxt(fname=filename, dtype="float", delimiter=",", skiprows=1)
    return data_set


def plot_scatter_diag(
    dataset: np.ndarray,
    title: str = "scatter diagram",
    label: str = "Observed data",
    xlabel: str = "x1",
    ylabel: str = "x2",
    zlabel: str = "x3",
):
    """新たにグラフ描画領域を作り、散布図をプロットする.

    Args:
        dataset (np.ndarray): csvデータ
        title (str, optional): グラフタイトル. Defaults to "scatter diagram".
        label (str, optional): 凡例. Default to "Observed data".
        xlabel (str, optional): X軸のラベル名. Defaults to "x1".
        ylabel (str, optional): Y軸のラベル名. Defaults to "x2".
        zlabel (str, optional): Z軸のラベル名. Defaults to "x3".

    Returns:
        ax: グラフの描画領域を示すAxisオブジェクト.
    """
    # グラフの次元を取得
    dim = len(dataset[0])

    # グラフ描画の設定
    fig = plt.figure()

    x1 = dataset[:, 0]
    x2 = dataset[:, 1]

    if dim == 2:  # x-yグラフ
        ax = fig.add_subplot(111)
        ax.scatter(x1, x2, label=label, color="b", marker=".")

    elif dim == 3:  # x-y-zグラフ
        x3 = dataset[:, 2]
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(x1, x2, x3, label=label, color="b", marker=".")

        ax.set_zlabel(zlabel)

    # グラフ描画の設定
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid()

    # plt.show()
    return ax


def plot_reg_model(
    dataset: np.ndarray,
    ax,
    dim: int = 2,
):
    """散布図に回帰モデルを重ねて表示する.

    Args:
        dataset (np.ndarray): 回帰モデルのデータ
        ax (Axis, optional): プロットを追加したい場所を示すAxisオブジェクト.
        dim (int, optional): 2Dグラフ or 3Dグラフ. Defaults to 2.

    Returns:
        ax: Axisオブジェクト
    """

    # if ax is None:
    #    fig = plt.figure()
    #    ax = fig.add_subplot(111, projection="3d")
    #    ax.grid()
    #    col = "blue"
    # else:
    #    col = "orange"

    # TODO: labelつくりたい
    label = "creating..."

    if dim == 2:  # x-yグラフ
        ax.scatter(
            dataset[0], dataset[1], color="orange", label=label, alpha=0.2, marker="."
        )

    elif dim == 3:  # x-y-zグラフ
        ax.scatter(
            dataset[0],
            dataset[1],
            dataset[2],
            color="orange",
            label=label,
            alpha=0.2,
            marker=".",
        )

    ax.legend()
    plt.show()
    return ax


def calc_ind_var(dataset: np.ndarray, N: int) -> np.ndarray:
    """線形回帰モデルの説明変数を示す配列を求める.

    Args:
        dataset (np.ndarray): csvデータ.
        N (int): 説明変数の次数.

    Returns:
        np.ndarray: 説明変数の配列.
    """
    # 行列X作成
    X = np.ones((len(dataset), 1), dtype=float)

    # 散布図の軸数（x-y / x-y-z）
    dim = len(dataset[0])

    if dim == 2:  # x-y: y = 1*w0 + x*w1 + x^2*w2 + x^3*w4 + ...
        for i in range(N):
            X = np.hstack((X, dataset[:, 0].reshape(-1, 1) ** (i + 1)))

    elif dim == 3:  # x-y-z: y = 1*w0 + x*w1 + y*w2 + x^2*w3 + y^2*w4 + ...
        for i in range(N):
            X = np.hstack((X, dataset[:, 0].reshape(-1, 1) ** (i + 1)))
            X = np.hstack((X, dataset[:, 1].reshape(-1, 1) ** (i + 1)))

    return X


def calc_weight(y: np.ndarray, X: np.ndarray, lamb: float = 0) -> np.ndarray:
    """回帰係数（重み）を計算する.

    Args:
        y (np.ndarray): 従属変数を表す行列.
        X (np.ndarray): 独立変数を表す行列.
        lamb (float, optional): 正則化係数. Defaults to 0.

    Returns:
        np.ndarray: 回帰係数.
    """
    # 単位行列の生成
    Ident_matrix = np.eye(X.shape[1], dtype=float)

    # 重みの計算
    w = np.linalg.inv(X.T @ X + lamb * Ident_matrix) @ X.T @ y

    return w


def calc_reg_model(
    dataset: np.ndarray, w: np.ndarray, N: int, point: int = 10000
) -> list:
    """回帰係数を用いて, 回帰モデルをプロットするためのデータを計算する.

    Args:
        dataset (np.ndarray): csvデータ.
        w (np.ndarray): 回帰係数（重み）.
        N (int): 回帰の次数.
        point (int, optional): プロット数(データが3次元の場合, point*point). Defaults to 10000.

    Returns:
        list: 回帰モデルのx軸, y軸(, z軸)をまとめたリスト.
    """
    # 散布図の軸数（x-y / x-y-z）
    dim = len(dataset[0])

    x = np.linspace(min(dataset[:, 0]), max(dataset[:, 0]), point)

    if dim == 2:  # x-y
        axis_x = np.ones((point, 1), dtype=float)
        for i in range(N):
            axis_x = np.hstack((axis_x, x.reshape(-1, 1) ** (i + 1)))
        fx = axis_x @ w  # y = Xw
        model_dataset = [x, fx]

    elif dim == 3:  # x-y-z
        y = np.linspace(min(dataset[:, 1]), max(dataset[:, 1]), point)
        XX, YY = np.meshgrid(x, y)

        # y = 1*w0 + x*w1 + y*w2 + x^2*w3 + y^2*w4 + ...
        fx = np.zeros((point, point))
        fx += w[0]  # 1*w0
        for i in range(N):  # x*w1 + y*w2 + x^2*w3 + y^2*w4 + ...
            fx += (XX ** (i + 1)) * w[(2 * i) + 1]
            fx += (YY ** (i + 1)) * w[(2 * i) + 2]
        model_dataset = [XX, YY, fx]

    return model_dataset


def create_reg_model(
    dataset: np.ndarray, N: int, lamb: float = 0, point: int = 10000
) -> list:
    """csvデータから回帰モデルを生成する.

    Args:
        dataset (np.ndarray): csvデータ.
        N (int): 回帰の次数.
        lamb (float, optional): 正則化係数. Defaults to 0.
        point (int, optional): 回帰モデルのプロット数(データが3次元の場合, point*point). Defaults to 10000.

    Returns:
        list: 回帰モデルのx軸, y軸(, z軸)をまとめたリスト.
    """
    # dim = len(dataset[0])

    y = dataset[:, -1].reshape(-1, 1)
    X = calc_ind_var(dataset, N)

    w = calc_weight(y, X, lamb)

    reg_model = calc_reg_model(dataset, w, N, point)

    return reg_model


def main():
    """csvファイルからデータを読み込み, 回帰分析を行う."""

    # csvファイル読み込み
    # data1 = load_data("data1.csv")
    # data2 = load_data("data2.csv")
    data3 = load_data("data3.csv")

    # 散布図のプロット
    # ax1 = plot_scatter_diag(data1)
    # ax2 = plot_scatter_diag(data2)
    ax3 = plot_scatter_diag(data3)

    # ep = y - (X @ w) 誤差項

    # reg_model1 = create_reg_model(data1, N=1)
    # reg_model2 = create_reg_model(data2, N=3)
    reg_model3 = create_reg_model(data3, N=10, point=100)

    # plot_reg_model(reg_model1, ax=ax1)
    # plot_reg_model(reg_model2, ax=ax2)
    plot_reg_model(reg_model3, ax=ax3, dim=3)

    # plt.show()


if __name__ == "__main__":
    main()