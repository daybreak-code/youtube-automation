document.addEventListener('DOMContentLoaded', function() {
    // 处理可编辑单元格
    const editableCells = document.querySelectorAll('.editable');
    editableCells.forEach(cell => {
        cell.addEventListener('dblclick', function() {
            const currentText = this.textContent;
            const input = document.createElement('textarea');
            input.value = currentText;
            input.classList.add('form-control');
            this.textContent = '';
            this.appendChild(input);
            input.focus();

            input.addEventListener('blur', async function() {
                const newValue = this.value;
                const field = cell.dataset.field;
                const row = cell.closest('tr');
                const id = row.dataset.id;

                try {
                    const response = await fetch(`/storyboards/${id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            field: field,
                            value: newValue
                        })
                    });

                    if (response.ok) {
                        cell.textContent = newValue;
                    } else {
                        cell.textContent = currentText;
                        alert('更新失败，请重试');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    cell.textContent = currentText;
                    alert('更新失败，请重试');
                }
            });
        });
    });

    // 处理新增分镜
    const createStoryboardBtn = document.getElementById('createStoryboardBtn');
    if (createStoryboardBtn) {
        createStoryboardBtn.addEventListener('click', async function() {
            const form = document.getElementById('createStoryboardForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('/storyboards', {
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
}); 