// 通用JavaScript功能

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化表单验证
    initFormValidation();
    
    // 初始化表格排序
    initTableSorting();
    
    // 显示当前时间
    updateCurrentTime();
    
    // 自动刷新数据（如果页面需要）
    if (document.querySelector('[data-auto-refresh]')) {
        startAutoRefresh();
    }
});

// 初始化Bootstrap工具提示
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 初始化表单验证
function initFormValidation() {
    // 为所有需要验证的表单添加事件监听
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// 初始化表格排序
function initTableSorting() {
    const sortableTables = document.querySelectorAll('table[data-sortable]');
    sortableTables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                sortTable(table, header.cellIndex, header.dataset.sort);
            });
        });
    });
}

// 表格排序函数
function sortTable(table, columnIndex, sortType = 'string') {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isAscending = !tbody.dataset.sorted || tbody.dataset.sorted !== `asc-${columnIndex}`;
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        let comparison = 0;
        if (sortType === 'number') {
            comparison = parseFloat(aValue) - parseFloat(bValue);
        } else if (sortType === 'date') {
            comparison = new Date(aValue) - new Date(bValue);
        } else {
            comparison = aValue.localeCompare(bValue);
        }
        
        return isAscending ? comparison : -comparison;
    });
    
    // 移除现有行
    rows.forEach(row => tbody.removeChild(row));
    
    // 添加排序后的行
    rows.forEach(row => tbody.appendChild(row));
    
    // 更新排序状态
    tbody.dataset.sorted = isAscending ? `asc-${columnIndex}` : `desc-${columnIndex}`;
    
    // 更新表头指示器
    updateSortIndicators(table, columnIndex, isAscending);
}

// 更新排序指示器
function updateSortIndicators(table, columnIndex, isAscending) {
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        header.classList.remove('sort-asc', 'sort-desc');
        if (index === columnIndex) {
            header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        }
    });
}

// 显示当前时间
function updateCurrentTime() {
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        const now = new Date();
        const timeString = now.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
        timeElement.textContent = timeString;
    }
}

// 自动刷新数据
function startAutoRefresh() {
    const refreshElement = document.querySelector('[data-auto-refresh]');
    const interval = parseInt(refreshElement.dataset.autoRefresh) || 30000; // 默认30秒
    
    setInterval(() => {
        refreshData();
    }, interval);
}

// 刷新页面数据
function refreshData() {
    // 这里可以根据需要实现数据刷新逻辑
    // 例如：通过AJAX获取最新数据并更新页面
    console.log('刷新数据...');
}

// 显示加载动画
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 加载中...';
    element.disabled = true;
    return originalContent;
}

// 隐藏加载动画
function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
    element.disabled = false;
}

// 显示Toast通知
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });
    toast.show();
    
    // 自动移除Toast元素
    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
}

// 创建Toast容器
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1060';
    document.body.appendChild(container);
    return container;
}

// 确认对话框
function confirmDialog(message, callback) {
    if (confirm(message)) {
        if (typeof callback === 'function') {
            callback();
        }
        return true;
    }
    return false;
}

// 复制到剪贴板
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('已复制到剪贴板', 'success');
    }).catch(err => {
        console.error('复制失败:', err);
        showToast('复制失败', 'danger');
    });
}

// 格式化时间
function formatTime(date) {
    if (!date) return '';
    
    const d = new Date(date);
    const now = new Date();
    const diff = now - d;
    
    // 如果是一天内
    if (diff < 24 * 60 * 60 * 1000) {
        if (diff < 60 * 60 * 1000) {
            return Math.floor(diff / (60 * 1000)) + '分钟前';
        }
        return Math.floor(diff / (60 * 60 * 1000)) + '小时前';
    }
    
    // 如果是今年内
    if (d.getFullYear() === now.getFullYear()) {
        return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
    }
    
    return d.toLocaleDateString('zh-CN');
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}