# CMAES_Tutorial

CMA-ES（Covariance Matrix Adaptation Evolution Strategy，协方差矩阵自适应进化策略）中文学习教程。

虽然 CMA-ES 的使用者很多，但系统、易读的中文学习资料仍然比较少。本仓库基于原作者用于教学的 Jupyter Notebook 整理并完成中文化，保留 CMA-ES 的标准英文术语、数学公式与参考文献，便于继续阅读原始论文。

建议按照编号顺序学习：`0_` → `1_` → `2_` → `3_` → `4_` → `5_` → `6_`。

## 推荐学习顺序

- `0_black_box_optimization.ipynb`：黑盒优化基础
- `1_evolution_strategy.ipynb`：Evolution Strategy 基础
- `2_step_size_adaptation.ipynb`：步长自适应与 CSA
- `3_covariance_matrix_adaptation.ipynb`：协方差矩阵自适应
- `4_nonseparability.ipynb`：不可分问题、完整协方差与旋转不变性
- `5_multimodality.ipynb`：多峰问题、种群规模与重启
- `6_advanced_adaptation_mechanisms.ipynb`：rank-one、active update、diagonal acceleration 与 dd-CMA
- `a1_minmax_optimization.ipynb`：Min-Max 优化、Adversarial-CMA-ES 与 WRA-CMA-ES
- `cmaes_acceleration.ipynb`：CMA-ES 工程加速与并行评估
- `cmaes_practical_guide.ipynb`：CMA-ES 实践配置、日志诊断与问题定式化

## 中文版说明

仓库中的 10 个 Notebook 已完成中文化。处理原则如下：

- Markdown 教学说明全部改为简体中文；
- 教学性 docstring 与代码注释尽量使用中文；
- `CMA-ES`、`CSA`、`rank-one update`、`active update`、`diagonal decoding` 等标准术语保留英文名称，首次出现时配合中文解释；
- 数学公式、算法符号和论文引用保持原意；
- `0`–`5` 主线教程尽量保持原有实验结构；
- 对 `6_advanced_adaptation_mechanisms.ipynb`、`a1_minmax_optimization.ipynb`、`cmaes_acceleration.ipynb` 和 `cmaes_practical_guide.ipynb` 中大量重复粘贴的外部实现与工程辅助代码进行了教学化整理：保留核心算法、关键实验与理论说明，并提供原实现链接，避免教程被重复源码淹没。

## 理解 CMA-ES 建议至少阅读的论文

以下论文均可通过机构仓储、作者主页或公开学术存档获取 PDF。

- Nikolaus Hansen, Andreas Ostermeier; *Completely Derandomized Self-Adaptation in Evolution Strategies*. Evol Comput 2001; 9 (2): 159–195. doi: https://doi.org/10.1162/106365601750190398
  - CMA-ES 的原型工作。提出了使用 CSA（Cumulative Step-size Adaptation，累积步长自适应）更新步长，并通过 rank-one 更新调整协方差矩阵的算法框架。

- Nikolaus Hansen, Sibylle D. Müller, Petros Koumoutsakos; *Reducing the Time Complexity of the Derandomized Evolution Strategy with Covariance Matrix Adaptation (CMA-ES)*. Evol Comput 2003; 11 (1): 1–18. doi: https://doi.org/10.1162/106365603321828970
  - 引入 rank-μ 更新，使算法能够更高效地利用较大的种群规模。

- Hansen, N., Kern, S. (2004). *Evaluating the CMA Evolution Strategy on Multimodal Test Functions*. In: Yao, X., et al. Parallel Problem Solving from Nature - PPSN VIII. PPSN 2004. Lecture Notes in Computer Science, vol 3242. Springer, Berlin, Heidelberg. https://doi.org/10.1007/978-3-540-30217-9_29
  - 研究 CMA-ES 在多峰函数上的性能。结果表明，增大种群规模通常能够提高发现全局最优解的概率，但对部分问题并不一定有效。该工作还引入了 weighted recombination，即根据排名对不同候选解赋予不同权重。它与多峰性本身没有直接关系，但通常比均匀权重略高效，因此后来被长期采用。

- G. A. Jastrebski and D. V. Arnold, *Improving Evolution Strategies through Active Covariance Matrix Adaptation*, 2006 IEEE International Conference on Evolutionary Computation, Vancouver, BC, Canada, 2006, pp. 2814-2821, doi: https://doi.org/10.1109/CEC.2006.1688662.
  - 提出 Active Covariance Matrix Adaptation，在协方差矩阵更新时利用负权重。传统 CMA-ES 更擅长学习较大的特征值，而 Active 更新能够提高较小特征值方向上的学习效率。

- Ros, R., Hansen, N. (2008). *A Simple Modification in CMA-ES Achieving Linear Time and Space Complexity*. In: Rudolph, G., Jansen, T., Beume, N., Lucas, S., Poloni, C. (eds) Parallel Problem Solving from Nature – PPSN X. PPSN 2008. Lecture Notes in Computer Science, vol 5199. Springer, Berlin, Heidelberg. https://doi.org/10.1007/978-3-540-87700-4_30
  - 提出 Sep-CMA-ES，将协方差矩阵限制为对角矩阵，从而使计算和存储复杂度相对于变量维数达到线性规模。它同时说明了：限制协方差结构会损失处理变量相关问题的能力，但在可分问题上可以显著加快尺度学习。

- Y. Akimoto, N. Hansen; *Diagonal Acceleration for Covariance Matrix Adaptation Evolution Strategies*. Evol Comput 2020; 28 (3): 405–435. doi: https://doi.org/10.1162/evco_a_00260
  - 提出 diagonal decoding，在传统 CMA-ES 与 Sep-CMA-ES 之间取得折中，并给出了 active update 中保持协方差正定性的框架。
