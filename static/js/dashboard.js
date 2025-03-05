// 테마 토글
document.getElementById('theme-toggle').addEventListener('click', function() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    body.setAttribute('data-theme', newTheme);
});

// 카드 클릭 이벤트
const riskLevelMap = {
    'high-risk-transactions': 'high',
    'medium-risk-transactions': 'medium',
    'low-risk-transactions': 'low'
};

document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', function() {
        const titleElement = this.querySelector('.card-title');
        if (!titleElement) return;

        const cardId = this.querySelector('h2')?.id;
        if (cardId && riskLevelMap[cardId]) {
            window.location.href = `/transactions/risk_level/${riskLevelMap[cardId]}`;
        }
    });
});

// 데이터 새로고침
function refreshData() {
    fetchTransactions();
    fetchStatistics();
    updateCharts();
}

// 거래 데이터 가져오기
async function fetchTransactions() {
    try {
        const response = await fetch('/api/transactions');
        const transactions = await response.json();
        updateTransactionTable(transactions);
    } catch (error) {
        console.error('거래 데이터 조회 실패:', error);
    }
}

// 통계 데이터 가져오기
async function fetchStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const stats = await response.json();
        updateStatistics(stats);
    } catch (error) {
        console.error('통계 데이터 조회 실패:', error);
    }
}

// 거래 테이블 업데이트
function updateTransactionTable(transactions) {
    const tbody = document.getElementById('transactions-table-body');
    tbody.innerHTML = '';

    transactions.forEach(t => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(t.timestamp).toLocaleString()}</td>
            <td>${t.source}</td>
            <td>${t.destination}</td>
            <td>${t.amount.toLocaleString()}원</td>
            <td>${(t.risk_score * 100).toFixed(1)}%</td>
            <td><span class="badge-risk ${t.risk_level.toLowerCase()}">${t.risk_level}</span></td>
        `;
        tbody.appendChild(row);
    });
}

// 통계 업데이트
function updateStatistics(stats) {
    const cards = [
        { id: 'total-transactions', value: stats.total_transactions },
        { id: 'high-risk-transactions', value: stats.risk_distribution.high },
        { id: 'medium-risk-transactions', value: stats.risk_distribution.medium },
        { id: 'low-risk-transactions', value: stats.risk_distribution.low }
    ];

    cards.forEach(card => {
        const element = document.getElementById(card.id);
        if (element) {
            element.textContent = card.value.toLocaleString();
        }
    });
}

// CSV 파일 업로드
document.getElementById('csv-upload').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (response.ok) {
            alert('거래 데이터가 성공적으로 업로드되었습니다.');
            refreshData();
        } else {
            alert('업로드 실패: ' + result.error);
        }
    } catch (error) {
        console.error('파일 업로드 실패:', error);
        alert('파일 업로드 중 오류가 발생했습니다.');
    }
});

// 초기 데이터 로드
document.addEventListener('DOMContentLoaded', function() {
    refreshData();
    // 30초마다 자동 새로고침
    setInterval(refreshData, 30000);
});
```
<replit_final_file>
```javascript