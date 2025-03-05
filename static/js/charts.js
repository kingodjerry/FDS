let riskDistributionChart;
let transactionTrendChart;

// 차트 초기화
function initializeCharts() {
    const riskCtx = document.getElementById('risk-distribution-chart').getContext('2d');
    const trendCtx = document.getElementById('transaction-trend-chart').getContext('2d');

    // 위험도 분포 차트
    riskDistributionChart = new Chart(riskCtx, {
        type: 'doughnut',
        data: {
            labels: ['고위험', '중위험', '저위험'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#dc3545', '#ffc107', '#198754']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // 거래 금액 추이 차트
    transactionTrendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '거래 금액',
                data: [],
                borderColor: '#0d6efd',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => value.toLocaleString() + '원'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// 차트 업데이트
async function updateCharts() {
    try {
        const [transactionsResponse, statsResponse] = await Promise.all([
            fetch('/api/transactions'),
            fetch('/api/statistics')
        ]);

        const transactions = await transactionsResponse.json();
        const stats = await statsResponse.json();

        // 위험도 분포 차트 업데이트
        riskDistributionChart.data.datasets[0].data = [
            stats.risk_distribution.high,
            stats.risk_distribution.medium,
            stats.risk_distribution.low
        ];
        riskDistributionChart.update();

        // 거래 금액 추이 차트 업데이트
        const recentTransactions = transactions.slice(0, 10).reverse();
        transactionTrendChart.data.labels = recentTransactions.map(t => 
            new Date(t.timestamp).toLocaleTimeString()
        );
        transactionTrendChart.data.datasets[0].data = recentTransactions.map(t => t.amount);
        transactionTrendChart.update();

    } catch (error) {
        console.error('차트 업데이트 실패:', error);
    }
}

// 차트 초기화 및 업데이트
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    updateCharts();
});
