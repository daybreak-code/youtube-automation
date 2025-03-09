document.addEventListener('DOMContentLoaded', function() {
    const createDraftBtn = document.getElementById('createDraftBtn');
    if (createDraftBtn) {
        createDraftBtn.addEventListener('click', async function() {
            const form = document.getElementById('createDraftForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('/drafts', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert('创建失败，请重试');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('创建失败，请重试');
            }
        });
    }

    // 处理单个折叠
    document.querySelectorAll('.collapse-icon').forEach(icon => {
        icon.addEventListener('click', function() {
            const row = this.closest('.draft-row');
            const content = row.nextElementSibling;
            
            // 切换显示/隐藏
            if (content.style.display === 'none') {
                content.style.display = 'table-row';
                this.classList.replace('bi-chevron-down', 'bi-chevron-up');
            } else {
                content.style.display = 'none';
                this.classList.replace('bi-chevron-up', 'bi-chevron-down');
            }
        });
    });

    // 处理全部折叠/展开
    const collapseAllBtn = document.getElementById('collapseAllBtn');
    if (collapseAllBtn) {
        collapseAllBtn.addEventListener('click', function() {
            const isCollapsed = this.classList.contains('bi-chevron-down');
            const contents = document.querySelectorAll('.collapse-content');
            const icons = document.querySelectorAll('.collapse-icon');
            
            contents.forEach(content => {
                content.style.display = isCollapsed ? 'table-row' : 'none';
            });
            
            icons.forEach(icon => {
                if (isCollapsed) {
                    icon.classList.replace('bi-chevron-down', 'bi-chevron-up');
                } else {
                    icon.classList.replace('bi-chevron-up', 'bi-chevron-down');
                }
            });
            
            // 切换全部折叠按钮图标
            this.classList.replace(
                isCollapsed ? 'bi-chevron-down' : 'bi-chevron-up',
                isCollapsed ? 'bi-chevron-up' : 'bi-chevron-down'
            );
        });
    }
}); 