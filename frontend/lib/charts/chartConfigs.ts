/**
 * 图表配置数据
 * @module lib/charts/chartConfigs
 * @description 定义所有支持的图表类型及其默认配置
 */

import type { EChartsOption } from 'echarts';
import type { ChartConfig, ChartCategory } from '@/types/visualization';

// ============================================
// 默认调色板
// ============================================

/**
 * 默认调色板配置
 * @description 提供统一的颜色方案
 */
const DEFAULT_COLOR_PALETTE = [
    '#5470c6',   // 蓝色
    '#91cc75',   // 绿色
    '#fac858',   // 黄色
    '#ee6666',   // 红色
    '#73c0de',   // 浅蓝
    '#3ba272',   // 深绿
    '#fc8452',   // 橙色
    '#9a60b4',   // 紫色
    '#ea7ccc',   // 粉色
    '#48b8d0'    // 青色
];

// ============================================
// 基础图表配置
// ============================================

/**
 * 柱状图配置
 * @description 用于比较不同类别的数据大小
 */
const barChartConfig: ChartConfig = {
    id: 'bar',
    type: 'bar',
    category: 'basic' as ChartCategory,
    name: '柱状图',
    nameEn: 'Bar Chart',
    icon: 'bar-chart-3',
    description: '使用矩形条表示数据大小的图表，适合比较不同类别之间的数值差异。',
    useCases: [
        '销售数据对比',
        '各类别数量统计',
        '多维度数据比较',
        '时间序列数据对比'
    ],
    dataRequirements: [
        '需要一个维度字段（X轴）',
        '至少一个度量字段（Y轴）',
        '支持多系列数据'
    ],
    defaultOption: {
        title: {
            text: '柱状图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['系列1'],
            top: 30
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: ['类别A', '类别B', '类别C', '类别D', '类别E']
        },
        yAxis: {
            type: 'value'
        },
        series: [
            {
                name: '系列1',
                type: 'bar',
                data: [120, 200, 150, 80, 70],
                itemStyle: {
                    color: DEFAULT_COLOR_PALETTE[0]
                }
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

/**
 * 折线图配置
 * @description 用于展示数据随时间或类别的变化趋势
 */
const lineChartConfig: ChartConfig = {
    id: 'line',
    type: 'line',
    category: 'basic' as ChartCategory,
    name: '折线图',
    nameEn: 'Line Chart',
    icon: 'trending-up',
    description: '用线段连接数据点展示趋势变化的图表，适合展示连续数据的变化规律。',
    useCases: [
        '时间序列数据分析',
        '趋势预测',
        '多指标对比趋势',
        '股票/气温等连续数据'
    ],
    dataRequirements: [
        '需要一个维度字段（X轴）',
        '至少一个度量字段（Y轴）',
        '数据最好按维度排序'
    ],
    defaultOption: {
        title: {
            text: '折线图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['系列1'],
            top: 30
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        },
        yAxis: {
            type: 'value'
        },
        series: [
            {
                name: '系列1',
                type: 'line',
                data: [820, 932, 901, 934, 1290, 1330, 1320],
                smooth: true,
                itemStyle: {
                    color: DEFAULT_COLOR_PALETTE[0]
                }
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

/**
 * 饼图配置
 * @description 用于展示各部分占整体的比例关系
 */
const pieChartConfig: ChartConfig = {
    id: 'pie',
    type: 'pie',
    category: 'basic' as ChartCategory,
    name: '饼图',
    nameEn: 'Pie Chart',
    icon: 'pie-chart',
    description: '用圆形展示各部分占整体比例的图表，适合展示构成比例和占比分析。',
    useCases: [
        '市场份额分析',
        '预算分配展示',
        '人口构成分析',
        '各类别占比统计'
    ],
    dataRequirements: [
        '需要一个类别字段',
        '需要一个数值字段',
        '数据应为正数'
    ],
    defaultOption: {
        title: {
            text: '饼图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            top: 'middle'
        },
        series: [
            {
                name: '访问来源',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false,
                    position: 'center'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 20,
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: [
                    { value: 1048, name: '搜索引擎' },
                    { value: 735, name: '直接访问' },
                    { value: 580, name: '邮件营销' },
                    { value: 484, name: '联盟广告' },
                    { value: 300, name: '视频广告' }
                ]
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

/**
 * 散点图配置
 * @description 用于展示两个变量之间的关系
 */
const scatterChartConfig: ChartConfig = {
    id: 'scatter',
    type: 'scatter',
    category: 'basic' as ChartCategory,
    name: '散点图',
    nameEn: 'Scatter Chart',
    icon: 'git-branch',
    description: '用点表示数据分布的图表，适合分析两个变量之间的相关性和分布规律。',
    useCases: [
        '相关性分析',
        '数据分布研究',
        '异常值检测',
        '回归分析'
    ],
    dataRequirements: [
        '需要两个数值字段（X轴和Y轴）',
        '可选的颜色分组字段',
        '可选的大小字段'
    ],
    defaultOption: {
        title: {
            text: '散点图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: function (params: unknown) {
                const p = params as { data: number[] };
                return `数据: (${p.data[0]}, ${p.data[1]})`;
            }
        },
        grid: {
            left: '3%',
            right: '7%',
            bottom: '7%',
            containLabel: true
        },
        xAxis: {
            type: 'value',
            splitLine: {
                show: true,
                lineStyle: {
                    type: 'dashed'
                }
            }
        },
        yAxis: {
            type: 'value',
            splitLine: {
                show: true,
                lineStyle: {
                    type: 'dashed'
                }
            }
        },
        series: [
            {
                name: '数据点',
                type: 'scatter',
                symbolSize: 10,
                data: [
                    [10.0, 8.04],
                    [8.07, 6.95],
                    [13.0, 7.58],
                    [9.05, 8.81],
                    [11.0, 8.33],
                    [14.0, 7.66],
                    [13.4, 6.81],
                    [10.0, 6.33],
                    [14.0, 8.96],
                    [12.5, 6.82]
                ],
                itemStyle: {
                    color: DEFAULT_COLOR_PALETTE[0]
                }
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

/**
 * 面积图配置
 * @description 用于展示数据随时间变化的累积效果
 */
const areaChartConfig: ChartConfig = {
    id: 'area',
    type: 'area',
    category: 'basic' as ChartCategory,
    name: '面积图',
    nameEn: 'Area Chart',
    icon: 'area-chart',
    description: '在折线图基础上填充区域的图表，适合展示累积效果和趋势变化。',
    useCases: [
        '累积销售额展示',
        '流量趋势分析',
        '资源使用量监控',
        '多指标堆叠对比'
    ],
    dataRequirements: [
        '需要一个维度字段（X轴）',
        '至少一个度量字段（Y轴）',
        '支持多系列堆叠'
    ],
    defaultOption: {
        title: {
            text: '面积图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                label: {
                    backgroundColor: '#6a7985'
                }
            }
        },
        legend: {
            data: ['系列1', '系列2'],
            top: 30
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: [
            {
                name: '系列1',
                type: 'line',
                stack: 'Total',
                areaStyle: {},
                emphasis: {
                    focus: 'series'
                },
                data: [120, 132, 101, 134, 90, 230, 210]
            },
            {
                name: '系列2',
                type: 'line',
                stack: 'Total',
                areaStyle: {},
                emphasis: {
                    focus: 'series'
                },
                data: [220, 182, 191, 234, 290, 330, 310]
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

/**
 * 雷达图配置
 * @description 用于多维度数据的对比分析
 */
const radarChartConfig: ChartConfig = {
    id: 'radar',
    type: 'radar',
    category: 'basic' as ChartCategory,
    name: '雷达图',
    nameEn: 'Radar Chart',
    icon: 'radar',
    description: '用多边形展示多维度数据的图表，适合进行多维度对比和能力评估。',
    useCases: [
        '员工能力评估',
        '产品特性对比',
        '绩效分析',
        '多维指标评价'
    ],
    dataRequirements: [
        '需要多个维度指标',
        '每个维度需要数值',
        '支持多系列对比'
    ],
    defaultOption: {
        title: {
            text: '雷达图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item'
        },
        legend: {
            data: ['预算分配', '实际开销'],
            top: 30
        },
        radar: {
            indicator: [
                { name: '销售', max: 6500 },
                { name: '管理', max: 16000 },
                { name: '信息技术', max: 30000 },
                { name: '客服', max: 38000 },
                { name: '研发', max: 52000 },
                { name: '市场', max: 25000 }
            ]
        },
        series: [
            {
                name: '预算 vs 开销',
                type: 'radar',
                data: [
                    {
                        value: [4200, 3000, 20000, 35000, 50000, 18000],
                        name: '预算分配'
                    },
                    {
                        value: [5000, 14000, 28000, 26000, 42000, 21000],
                        name: '实际开销'
                    }
                ]
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

/**
 * 仪表盘配置
 * @description 用于展示单个指标的完成进度
 */
const gaugeChartConfig: ChartConfig = {
    id: 'gauge',
    type: 'gauge',
    category: 'basic' as ChartCategory,
    name: '仪表盘',
    nameEn: 'Gauge Chart',
    icon: 'gauge',
    description: '用仪表盘形式展示指标进度的图表，适合展示KPI完成度和进度状态。',
    useCases: [
        'KPI完成度展示',
        '目标达成率',
        '设备状态监控',
        '健康度评分'
    ],
    dataRequirements: [
        '需要一个数值指标',
        '需要定义最大值范围',
        '可选的阈值分段'
    ],
    defaultOption: {
        title: {
            text: '仪表盘示例',
            left: 'center'
        },
        series: [
            {
                type: 'gauge',
                center: ['50%', '60%'],
                startAngle: 200,
                endAngle: -20,
                min: 0,
                max: 100,
                splitNumber: 10,
                itemStyle: {
                    color: DEFAULT_COLOR_PALETTE[0]
                },
                progress: {
                    show: true,
                    width: 30
                },
                pointer: {
                    show: false
                },
                axisLine: {
                    lineStyle: {
                        width: 30
                    }
                },
                axisTick: {
                    distance: -45,
                    splitNumber: 5,
                    lineStyle: {
                        width: 2,
                        color: '#999'
                    }
                },
                splitLine: {
                    distance: -52,
                    length: 14,
                    lineStyle: {
                        width: 3,
                        color: '#999'
                    }
                },
                axisLabel: {
                    distance: -20,
                    color: '#999',
                    fontSize: 12
                },
                anchor: {
                    show: false
                },
                title: {
                    show: false
                },
                detail: {
                    valueAnimation: true,
                    width: '60%',
                    lineHeight: 40,
                    borderRadius: 8,
                    offsetCenter: [0, '-15%'],
                    fontSize: 30,
                    fontWeight: 'bolder',
                    formatter: '{value}%',
                    color: 'inherit'
                },
                data: [
                    {
                        value: 75
                    }
                ]
            }
        ]
    } as EChartsOption
};

// ============================================
// 统计图表配置
// ============================================

/**
 * 热力图配置
 * @description 用于展示二维数据的密度分布
 */
const heatmapChartConfig: ChartConfig = {
    id: 'heatmap',
    type: 'heatmap',
    category: 'statistical' as ChartCategory,
    name: '热力图',
    nameEn: 'Heatmap Chart',
    icon: 'flame',
    description: '用颜色深浅表示数据密度的图表，适合展示二维数据的分布规律。',
    useCases: [
        '用户行为热力分析',
        '时间分布统计',
        '网站点击热力图',
        '数据密度展示'
    ],
    dataRequirements: [
        '需要两个维度字段',
        '需要一个数值字段',
        '数据适合网格化展示'
    ],
    defaultOption: {
        title: {
            text: '热力图示例',
            left: 'center'
        },
        tooltip: {
            position: 'top'
        },
        grid: {
            top: 60,
            bottom: 60
        },
        xAxis: {
            type: 'category',
            data: ['12a', '1a', '2a', '3a', '4a', '5a', '6a'],
            splitArea: {
                show: true
            }
        },
        yAxis: {
            type: 'category',
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            splitArea: {
                show: true
            }
        },
        visualMap: {
            min: 0,
            max: 10,
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: 0
        },
        series: [
            {
                name: '访问量',
                type: 'heatmap',
                data: [
                    [0, 0, 5], [0, 1, 1], [0, 2, 0], [0, 3, 0], [0, 4, 0],
                    [1, 0, 7], [1, 1, 0], [1, 2, 0], [1, 3, 0], [1, 4, 0],
                    [2, 0, 1], [2, 1, 1], [2, 2, 0], [2, 3, 0], [2, 4, 0],
                    [3, 0, 7], [3, 1, 3], [3, 2, 0], [3, 3, 0], [3, 4, 0],
                    [4, 0, 1], [4, 1, 3], [4, 2, 0], [4, 3, 0], [4, 4, 0]
                ],
                label: {
                    show: true
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    } as EChartsOption
};

/**
 * 漏斗图配置
 * @description 用于展示流程转化率
 */
const funnelChartConfig: ChartConfig = {
    id: 'funnel',
    type: 'funnel',
    category: 'statistical' as ChartCategory,
    name: '漏斗图',
    nameEn: 'Funnel Chart',
    icon: 'filter',
    description: '用漏斗形状展示流程转化的图表，适合分析转化率和流失情况。',
    useCases: [
        '销售漏斗分析',
        '用户转化率',
        '招聘流程统计',
        '营销效果追踪'
    ],
    dataRequirements: [
        '需要阶段名称字段',
        '需要数值字段',
        '数据应按流程顺序排列'
    ],
    defaultOption: {
        title: {
            text: '漏斗图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b} : {c}%'
        },
        series: [
            {
                name: '漏斗图',
                type: 'funnel',
                left: '10%',
                top: 60,
                bottom: 60,
                width: '80%',
                min: 0,
                max: 100,
                minSize: '0%',
                maxSize: '100%',
                sort: 'descending',
                gap: 2,
                label: {
                    show: true,
                    position: 'inside'
                },
                labelLine: {
                    length: 10,
                    lineStyle: {
                        width: 1,
                        type: 'solid'
                    }
                },
                itemStyle: {
                    borderColor: '#fff',
                    borderWidth: 1
                },
                emphasis: {
                    label: {
                        fontSize: 20
                    }
                },
                data: [
                    { value: 100, name: '展现' },
                    { value: 80, name: '点击' },
                    { value: 60, name: '访问' },
                    { value: 40, name: '咨询' },
                    { value: 20, name: '订单' }
                ]
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

/**
 * 矩形树图配置
 * @description 用于展示层级数据的占比关系
 */
const treemapChartConfig: ChartConfig = {
    id: 'treemap',
    type: 'treemap',
    category: 'statistical' as ChartCategory,
    name: '矩形树图',
    nameEn: 'Treemap Chart',
    icon: 'layout-grid',
    description: '用矩形面积展示层级数据占比的图表，适合分析多层级数据的构成。',
    useCases: [
        '文件系统空间分析',
        '预算分配展示',
        '市场份额分析',
        '组织架构展示'
    ],
    dataRequirements: [
        '需要层级结构数据',
        '每个节点需要数值',
        '支持多层级嵌套'
    ],
    defaultOption: {
        title: {
            text: '矩形树图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item'
        },
        series: [
            {
                type: 'treemap',
                data: [
                    {
                        name: '节点A',
                        value: 10,
                        children: [
                            {
                                name: '子节点A1',
                                value: 4
                            },
                            {
                                name: '子节点A2',
                                value: 6
                            }
                        ]
                    },
                    {
                        name: '节点B',
                        value: 20,
                        children: [
                            {
                                name: '子节点B1',
                                value: 10
                            },
                            {
                                name: '子节点B2',
                                value: 10
                            }
                        ]
                    }
                ]
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

/**
 * 旭日图配置
 * @description 用于展示多层级数据的环形占比
 */
const sunburstChartConfig: ChartConfig = {
    id: 'sunburst',
    type: 'sunburst',
    category: 'statistical' as ChartCategory,
    name: '旭日图',
    nameEn: 'Sunburst Chart',
    icon: 'sun',
    description: '用环形展示多层级数据占比的图表，适合分析层级结构和数据构成。',
    useCases: [
        '组织架构展示',
        '产品分类分析',
        '文件目录结构',
        '预算层级分配'
    ],
    dataRequirements: [
        '需要层级结构数据',
        '每个节点需要数值',
        '支持多层级嵌套'
    ],
    defaultOption: {
        title: {
            text: '旭日图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item'
        },
        series: [
            {
                type: 'sunburst',
                data: [
                    {
                        name: 'Grandpa',
                        value: 10,
                        children: [
                            {
                                name: 'Father',
                                value: 5,
                                children: [
                                    {
                                        name: 'Son',
                                        value: 2
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        name: 'Grandma',
                        value: 8,
                        children: [
                            {
                                name: 'Mother',
                                value: 4
                            }
                        ]
                    }
                ],
                radius: [0, '90%'],
                label: {
                    rotate: 'radial'
                }
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

/**
 * 桑基图配置
 * @description 用于展示数据流向和转化
 */
const sankeyChartConfig: ChartConfig = {
    id: 'sankey',
    type: 'sankey',
    category: 'statistical' as ChartCategory,
    name: '桑基图',
    nameEn: 'Sankey Chart',
    icon: 'git-merge',
    description: '用流向展示数据转化的图表，适合分析数据流动和转化路径。',
    useCases: [
        '用户行为路径分析',
        '能源流向分析',
        '资金流向追踪',
        '转化路径分析'
    ],
    dataRequirements: [
        '需要节点数据',
        '需要连接关系数据',
        '每条连接需要流量值'
    ],
    defaultOption: {
        title: {
            text: '桑基图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove'
        },
        series: [
            {
                type: 'sankey',
                layout: 'none',
                emphasis: {
                    focus: 'adjacency'
                },
                data: [
                    { name: 'a' },
                    { name: 'b' },
                    { name: 'c' },
                    { name: 'd' },
                    { name: 'e' }
                ],
                links: [
                    { source: 'a', target: 'b', value: 5 },
                    { source: 'a', target: 'c', value: 3 },
                    { source: 'b', target: 'd', value: 4 },
                    { source: 'c', target: 'd', value: 2 },
                    { source: 'd', target: 'e', value: 6 }
                ],
                lineStyle: {
                    color: 'gradient',
                    curveness: 0.5
                }
            }
        ]
    } as EChartsOption
};

// ============================================
// 地图图表配置
// ============================================

/**
 * 中国地图配置
 * @description 用于展示中国各省份的数据分布
 */
const chinaMapChartConfig: ChartConfig = {
    id: 'map_china',
    type: 'map_china',
    category: 'map' as ChartCategory,
    name: '中国地图',
    nameEn: 'China Map',
    icon: 'map',
    description: '在中国地图上展示各省份数据的图表，适合分析地域分布和区域对比。',
    useCases: [
        '销售区域分析',
        '人口分布展示',
        '疫情数据地图',
        '物流网络分析'
    ],
    dataRequirements: [
        '需要省份名称字段',
        '需要一个数值字段',
        '省份名称需标准化'
    ],
    defaultOption: {
        title: {
            text: '中国地图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{b}<br/>{c}'
        },
        visualMap: {
            min: 0,
            max: 100,
            left: 'left',
            top: 'bottom',
            text: ['高', '低'],
            calculable: true
        },
        series: [
            {
                name: '数据',
                type: 'map',
                map: 'china',
                roam: true,
                label: {
                    show: true
                },
                data: [
                    { name: '北京', value: 100 },
                    { name: '上海', value: 90 },
                    { name: '广东', value: 80 },
                    { name: '浙江', value: 70 },
                    { name: '江苏', value: 60 }
                ]
            }
        ]
    } as EChartsOption
};

/**
 * 世界地图配置
 * @description 用于展示全球各国家的数据分布
 */
const worldMapChartConfig: ChartConfig = {
    id: 'map_world',
    type: 'map_world',
    category: 'map' as ChartCategory,
    name: '世界地图',
    nameEn: 'World Map',
    icon: 'globe',
    description: '在世界地图上展示各国家数据的图表，适合分析全球分布和国际对比。',
    useCases: [
        '全球销售分析',
        '国际用户分布',
        '全球经济数据',
        '跨国业务分析'
    ],
    dataRequirements: [
        '需要国家名称字段',
        '需要一个数值字段',
        '国家名称需标准化'
    ],
    defaultOption: {
        title: {
            text: '世界地图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{b}<br/>{c}'
        },
        visualMap: {
            min: 0,
            max: 100,
            left: 'left',
            top: 'bottom',
            text: ['高', '低'],
            calculable: true
        },
        series: [
            {
                name: '数据',
                type: 'map',
                map: 'world',
                roam: true,
                label: {
                    show: false
                },
                data: [
                    { name: 'China', value: 100 },
                    { name: 'United States', value: 90 },
                    { name: 'Japan', value: 80 },
                    { name: 'Germany', value: 70 },
                    { name: 'United Kingdom', value: 60 }
                ]
            }
        ]
    } as EChartsOption
};

// ============================================
// 关系图表配置
// ============================================

/**
 * 关系图配置
 * @description 用于展示节点之间的关系网络
 */
const graphChartConfig: ChartConfig = {
    id: 'graph',
    type: 'graph',
    category: 'relation' as ChartCategory,
    name: '关系图',
    nameEn: 'Graph Chart',
    icon: 'network',
    description: '用节点和连线展示关系的图表，适合分析社交网络和组织关系。',
    useCases: [
        '社交网络分析',
        '组织架构展示',
        '知识图谱',
        '网络拓扑分析'
    ],
    dataRequirements: [
        '需要节点数据',
        '需要连接关系数据',
        '可选的节点大小/颜色字段'
    ],
    defaultOption: {
        title: {
            text: '关系图示例',
            left: 'center'
        },
        tooltip: {},
        series: [
            {
                type: 'graph',
                layout: 'force',
                data: [
                    { name: '节点1', symbolSize: 50 },
                    { name: '节点2', symbolSize: 40 },
                    { name: '节点3', symbolSize: 30 },
                    { name: '节点4', symbolSize: 20 }
                ],
                links: [
                    { source: '节点1', target: '节点2' },
                    { source: '节点1', target: '节点3' },
                    { source: '节点2', target: '节点4' },
                    { source: '节点3', target: '节点4' }
                ],
                roam: true,
                label: {
                    show: true,
                    position: 'right',
                    formatter: '{b}'
                },
                labelLayout: {
                    hideOverlap: true
                },
                force: {
                    repulsion: 100,
                    edgeLength: 100
                }
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

/**
 * 树图配置
 * @description 用于展示层级结构数据
 */
const treeChartConfig: ChartConfig = {
    id: 'tree',
    type: 'tree',
    category: 'relation' as ChartCategory,
    name: '树图',
    nameEn: 'Tree Chart',
    icon: 'git-branch',
    description: '用树形结构展示层级关系的图表，适合分析组织架构和分类体系。',
    useCases: [
        '组织架构展示',
        '文件目录结构',
        '决策树分析',
        '分类体系展示'
    ],
    dataRequirements: [
        '需要层级结构数据',
        '每个节点需要名称',
        '支持多层级嵌套'
    ],
    defaultOption: {
        title: {
            text: '树图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove'
        },
        series: [
            {
                type: 'tree',
                data: [
                    {
                        name: '根节点',
                        children: [
                            {
                                name: '子节点1',
                                children: [
                                    { name: '叶子节点1' },
                                    { name: '叶子节点2' }
                                ]
                            },
                            {
                                name: '子节点2',
                                children: [
                                    { name: '叶子节点3' }
                                ]
                            }
                        ]
                    }
                ],
                left: '2%',
                right: '2%',
                top: '8%',
                bottom: '20%',
                symbol: 'emptyCircle',
                orient: 'vertical',
                expandAndCollapse: true,
                label: {
                    position: 'top',
                    verticalAlign: 'middle',
                    align: 'center',
                    fontSize: 12
                },
                leaves: {
                    label: {
                        position: 'bottom',
                        verticalAlign: 'middle',
                        align: 'center'
                    }
                },
                animationDurationUpdate: 750
            }
        ]
    } as EChartsOption
};

// ============================================
// 特殊图表配置
// ============================================

/**
 * K线图配置
 * @description 用于展示股票等金融数据的开盘收盘价
 */
const candlestickChartConfig: ChartConfig = {
    id: 'candlestick',
    type: 'candlestick',
    category: 'special' as ChartCategory,
    name: 'K线图',
    nameEn: 'Candlestick Chart',
    icon: 'candlestick-chart',
    description: '用蜡烛形状展示股票价格走势的图表，适合金融数据分析和交易决策。',
    useCases: [
        '股票走势分析',
        '期货价格分析',
        '外汇交易分析',
        '金融数据可视化'
    ],
    dataRequirements: [
        '需要时间字段',
        '需要开盘价、收盘价、最低价、最高价',
        '数据按时间排序'
    ],
    defaultOption: {
        title: {
            text: 'K线图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%'
        },
        xAxis: {
            type: 'category',
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
            axisLine: { lineStyle: { color: '#777' } }
        },
        yAxis: {
            scale: true,
            splitArea: {
                show: true
            }
        },
        dataZoom: [
            {
                type: 'inside',
                start: 50,
                end: 100
            },
            {
                show: true,
                type: 'slider',
                top: '90%',
                start: 50,
                end: 100
            }
        ],
        series: [
            {
                type: 'candlestick',
                data: [
                    [2320.26, 2320.26, 2287.3, 2362.94],
                    [2300, 2291.3, 2288.26, 2308.38],
                    [2295.35, 2346.5, 2295.35, 2346.92],
                    [2347.22, 2358.98, 2337.35, 2363.8],
                    [2360.75, 2382.48, 2347.89, 2383.76]
                ]
            }
        ]
    } as EChartsOption
};

/**
 * 气泡图配置
 * @description 用于展示三维数据关系
 */
const bubbleChartConfig: ChartConfig = {
    id: 'bubble',
    type: 'scatter',
    category: 'special' as ChartCategory,
    name: '气泡图',
    nameEn: 'Bubble Chart',
    icon: 'circle-dot',
    description: '用气泡大小表示第三维度的散点图，适合分析三维数据关系。',
    useCases: [
        '市场分析（价格、销量、利润）',
        '人口数据分析',
        '产品组合分析',
        '投资组合分析'
    ],
    dataRequirements: [
        '需要X轴数值字段',
        '需要Y轴数值字段',
        '需要气泡大小字段',
        '可选的颜色分组字段'
    ],
    defaultOption: {
        title: {
            text: '气泡图示例',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: function (params: unknown) {
                const p = params as { data: number[] };
                return `X: ${p.data[0]}<br/>Y: ${p.data[1]}<br/>大小: ${p.data[2]}`;
            }
        },
        grid: {
            left: '3%',
            right: '7%',
            bottom: '7%',
            containLabel: true
        },
        xAxis: {
            splitLine: {
                lineStyle: {
                    type: 'dashed'
                }
            }
        },
        yAxis: {
            splitLine: {
                lineStyle: {
                    type: 'dashed'
                }
            },
            scale: true
        },
        series: [
            {
                name: '气泡',
                type: 'scatter',
                symbolSize: function (data: number[]) {
                    // 气泡大小根据第三个值计算
                    return Math.sqrt(data[2]) * 2;
                },
                data: [
                    [10.0, 8.04, 10],
                    [8.07, 6.95, 20],
                    [13.0, 7.58, 30],
                    [9.05, 8.81, 15],
                    [11.0, 8.33, 25]
                ],
                itemStyle: {
                    color: DEFAULT_COLOR_PALETTE[0],
                    opacity: 0.7
                }
            }
        ],
        color: DEFAULT_COLOR_PALETTE
    } as EChartsOption
};

// ============================================
// 图表配置数组
// ============================================

/**
 * 所有图表配置数组
 * @description 包含所有支持的图表类型配置
 */
export const chartConfigs: ChartConfig[] = [
    // 基础图表
    barChartConfig,
    lineChartConfig,
    pieChartConfig,
    scatterChartConfig,
    areaChartConfig,
    radarChartConfig,
    gaugeChartConfig,
    // 统计图表
    heatmapChartConfig,
    funnelChartConfig,
    treemapChartConfig,
    sunburstChartConfig,
    sankeyChartConfig,
    // 地图图表
    chinaMapChartConfig,
    worldMapChartConfig,
    // 关系图表
    graphChartConfig,
    treeChartConfig,
    // 特殊图表
    candlestickChartConfig,
    bubbleChartConfig
];

// ============================================
// 工具函数
// ============================================

/**
 * 根据图表类型获取配置
 * @param type - 图表类型
 * @returns 图表配置或undefined
 */
export function getChartConfigByType(type: string): ChartConfig | undefined {
    // 遍历配置数组查找匹配类型
    return chartConfigs.find(config => config.type === type);
}

/**
 * 根据分类获取图表配置列表
 * @param category - 图表分类
 * @returns 该分类下的图表配置数组
 */
export function getChartConfigsByCategory(category: ChartCategory): ChartConfig[] {
    // 过滤指定分类的图表配置
    return chartConfigs.filter(config => config.category === category);
}

/**
 * 获取所有图表分类
 * @returns 图表分类数组
 */
export function getAllCategories(): ChartCategory[] {
    // 返回所有唯一的分类
    const categories = new Set<ChartCategory>();
    chartConfigs.forEach(config => categories.add(config.category));
    return Array.from(categories);
}

/**
 * 搜索图表配置
 * @param keyword - 搜索关键词
 * @returns 匹配的图表配置数组
 */
export function searchChartConfigs(keyword: string): ChartConfig[] {
    // 转换为小写进行不区分大小写搜索
    const lowerKeyword = keyword.toLowerCase();
    return chartConfigs.filter(config => {
        // 搜索名称、描述、使用场景
        return (
            config.name.toLowerCase().includes(lowerKeyword) ||
            config.nameEn.toLowerCase().includes(lowerKeyword) ||
            config.description.toLowerCase().includes(lowerKeyword) ||
            config.useCases.some(uc => uc.toLowerCase().includes(lowerKeyword))
        );
    });
}

/**
 * 获取默认调色板
 * @returns 调色板颜色数组
 */
export function getDefaultColorPalette(): string[] {
    // 返回默认调色板的副本
    return [...DEFAULT_COLOR_PALETTE];
}
