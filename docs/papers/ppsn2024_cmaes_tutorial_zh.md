# PPSN 2024 CMA-ES Tutorial 中文解读

> 原始 HAL 条目：`hal-04709819`  
> 作者公开 slides：Nikolaus Hansen, **CMA-ES: Covariance Matrix Adaptation Evolution Strategy**, PPSN 2024 Tutorial, Hagenberg, Austria, September 2024.

## 1. 这份材料是什么

这不是一篇提出单一新算法的研究论文，而是一套由 CMA-ES 核心作者 Nikolaus Hansen 在 PPSN 2024 使用的系统教程。它的价值在于把 CMA-ES 的设计逻辑从“为什么需要随机连续优化”一路推进到“为什么要同时学习均值、协方差矩阵和全局步长”，非常适合作为本仓库 Notebook 的理论主线参考。

与只记忆 CMA-ES 更新公式相比，这份教程更强调三个问题：

1. **搜索分布应该如何表示当前对问题结构的认识？**
2. **为什么协方差矩阵可以被理解为一种二阶几何信息？**
3. **为什么步长 `sigma` 必须与协方差矩阵 `C` 分开自适应？**

## 2. CMA-ES 的核心视角：优化的是一个搜索分布

对于黑盒目标函数

$$
\min_{x\in\mathbb{R}^n} f(x),
$$

CMA-ES 并不直接维护一个确定性的搜索方向，而是维护高斯搜索分布

$$
x_k^{(g+1)} = m^{(g)} + \sigma^{(g)} y_k^{(g+1)},\qquad
y_k^{(g+1)} \sim \mathcal N(0,C^{(g)}).
$$

三个参数承担不同职责：

- `m`：搜索中心，决定“去哪里”；
- `C`：搜索形状和方向，决定“沿哪些组合方向搜索”；
- `sigma`：全局尺度，决定“迈多大一步”。

理解这一分工是理解整个 CMA-ES 的关键。

## 3. 从 selection + recombination 到均值更新

每一代采样 `lambda` 个候选点并按目标函数值排序。前 `mu` 个样本通过加权重组更新均值：

$$
m^{(g+1)} = \sum_{i=1}^{\mu} w_i x_{i:\lambda}^{(g+1)}.
$$

等价地，均值位移可以写成

$$
y_w^{(g+1)} = \sum_{i=1}^{\mu} w_i y_{i:\lambda}^{(g+1)}.
$$

这里真正重要的不是“平均若干优胜者”，而是：**排序后的成功搜索步包含了目标函数局部几何的信息。** 后续的 covariance adaptation 和 evolution path 都是在利用这些成功方向。

## 4. 为什么需要协方差矩阵自适应

如果只使用各向同性高斯分布，算法只能改变整体尺度，无法有效处理变量尺度差异和变量耦合。

协方差矩阵 `C` 允许搜索椭球发生旋转和拉伸，因此能够学习：

- 不同变量方向的合理尺度；
- 变量之间的相关性；
- 狭长谷地、ridge、非可分问题中的有效搜索方向。

在局部二次问题

$$
f(x)\approx \frac12(x-x^*)^T H(x-x^*),
$$

附近，理想的搜索分布形状与 `H^{-1}` 的几何结构密切相关。因此 CMA-ES 常被理解为一种**不需要梯度和 Hessian、但能够从函数值排序中学习近似二阶结构的随机优化方法**。

这也是它与简单随机搜索、固定协方差 ES 的本质区别。

## 5. Rank-mu update：从一代优胜样本学习局部形状

Rank-`mu` 更新利用当前一代多个成功搜索步更新协方差：

$$
C \leftarrow (1-c_\mu)C + c_\mu\sum_{i=1}^{\mu}w_i y_{i:\lambda}y_{i:\lambda}^T.
$$

直观上，每一个外积

$$
y_i y_i^T
$$

都会增加沿 `y_i` 方向的方差。多个优胜方向共同形成对局部搜索几何的估计。

因此 rank-`mu` 更新主要利用的是**同一代中的横向信息**。

## 6. Evolution Path 与 Rank-one update：利用跨代信息

如果连续若干代的均值更新方向大体一致，把每一代看成独立样本会浪费信息。

CMA-ES 使用 evolution path 累积这些方向：

$$
p_c \leftarrow (1-c_c)p_c + \sqrt{c_c(2-c_c)\mu_{\rm eff}}\, y_w.
$$

然后用

$$
p_c p_c^T
$$

进行 rank-one covariance update。

这可以理解为：

> 如果优化器连续多代朝某个方向移动，那么这个方向比单代随机波动更可信，应当逐渐扩大该方向的搜索尺度。

因此：

- rank-`mu`：主要使用当前种群信息；
- rank-one：主要使用跨代历史信息；
- 二者结合，使 `C` 同时具有较快适应速度和较低估计噪声。

## 7. 为什么 `sigma` 要独立于 `C`

这是教程中特别值得注意的一点。

数学上，可以把整体尺度吸收到协方差矩阵中，但 CMA-ES 明确写成

$$
\sigma^2 C.
$$

原因在于**整体步长变化与分布形状学习的时间尺度不同**。

- `C` 学习变量相关性和各向异性结构，需要相对稳定的统计估计；
- `sigma` 需要能够快速扩张或收缩搜索范围。

如果二者完全耦合，协方差矩阵必须同时承担“形状”和“尺度”两个任务，适应速度会明显受到限制。

## 8. CSA：用 evolution path 控制步长

Cumulative Step-size Adaptation（CSA）的核心不是直接观察目标函数值差异，而是观察**归一化搜索路径是否表现得像独立标准正态随机步**。

构造步长 evolution path：

$$
p_\sigma \leftarrow
(1-c_\sigma)p_\sigma
+
\sqrt{c_\sigma(2-c_\sigma)\mu_{\rm eff}}\,C^{-1/2}y_w.
$$

然后比较路径长度

$$
\|p_\sigma\|
$$

与标准正态向量期望长度

$$
E\|\mathcal N(0,I)\|.
$$

若路径明显偏长，表示连续步骤方向存在相关性，通常说明步长偏小，应增大 `sigma`；反之缩小 `sigma`。

典型更新形式为

$$
\sigma \leftarrow \sigma
\exp\left[
\frac{c_\sigma}{d_\sigma}
\left(
\frac{\|p_\sigma\|}{E\|\mathcal N(0,I)\|}-1
\right)
\right].
$$

## 9. CMA-ES 最重要的 invariance

CMA-ES 的强大不只来自更新公式，还来自它的 invariance 设计。

### 9.1 对严格单调目标变换不变

算法主要依赖候选解排序，因此把目标函数替换成

$$
g(f(x))
$$

只要 `g` 严格单调，搜索行为保持不变。

这意味着 CMA-ES 对目标函数数值尺度相对不敏感。

### 9.2 对搜索空间旋转具有良好的不变性

完整 covariance CMA-ES 能适应坐标旋转后的同一个问题。对于非可分问题，这一点非常重要，也是 `sep-CMA-ES` 等受限协方差版本与完整 CMA-ES 的主要差异之一。

## 10. 与经典二阶方法的关系

把 CMA-ES 简单描述为“进化算法”容易低估它。

从数值优化角度，更有帮助的理解是：

> CMA-ES 是一种仅使用函数值排序、通过随机采样学习搜索空间度量的自适应 variable-metric 方法。

它和 BFGS / Newton 方法的共同目标都是修正搜索空间的几何尺度；区别在于 CMA-ES：

- 不需要解析梯度；
- 不需要 Hessian；
- 能处理噪声、不连续和局部非光滑问题；
- 代价是通常需要更多函数评估。

因此，在光滑凸问题上，如果梯度方法可靠，CMA-ES 通常不是首选；它真正有优势的是困难的连续黑盒优化。

## 11. 与本仓库 Notebook 的对应关系

建议读完 Notebook 后按下面顺序回看这套 slides：

| 本仓库内容 | PPSN 2024 Tutorial 中对应的核心概念 |
|---|---|
| `1_evolution_strategy.ipynb` | sampling, selection, recombination |
| `2_step_size_adaptation.ipynb` | step-size control, CSA, evolution path |
| `3_covariance_matrix_adaptation.ipynb` | rank-mu / rank-one covariance update |
| `4_nonseparability.ipynb` | covariance geometry, rotational invariance |
| `5_multimodality.ipynb` | population size, global search and restarts |
| `6_advanced_adaptation_mechanisms.ipynb` | active update and advanced covariance adaptation |
| `cmaes_practical_guide.ipynb` | initialization, diagnostics and practical use |

## 12. 一句话理解 CMA-ES

CMA-ES 的核心不是“随机生成很多点再选最好的”，而是：

**把成功的随机搜索步当作统计观测，从这些观测中在线学习一个越来越合适的搜索坐标系，并独立控制全局搜索尺度。**

也可以写成：

$$
\boxed{
\text{CMA-ES}
=
\text{rank-based selection}
+
\text{distribution learning}
+
\text{covariance geometry}
+
\text{step-size adaptation}
}
$$

## 13. 来源

- HAL: https://inria.hal.science/hal-04709819/document
- Nikolaus Hansen, PPSN 2024 CMA-ES Tutorial slides: https://www.cmap.polytechnique.fr/~nikolaus.hansen/CMATutorialPPSN2024.pdf
- CMA-ES official site: https://cma-es.github.io/
- Written tutorial: Nikolaus Hansen, *The CMA Evolution Strategy: A Tutorial*, arXiv:1604.00772.
