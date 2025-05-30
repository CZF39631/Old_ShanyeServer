const API_URL = {
    修改备案: '/商标库/api/v1/修改备案',
    商标库查询: '/商标库/api/v1/商标库查询',
    商标库翻页: '/商标库/api/v1/商标库翻页',
    插入商标: '/商标库/api/v1/插入商标',
    更新商标信息: '/商标库/api/v1/更新商标信息',
    申请号查询: '/商标库/api/v1/申请号查询',
};

document.addEventListener('DOMContentLoaded', function () {
    const 存储模式 = localStorage.getItem('搜索模式') || '商标';
    const buttons = document.querySelectorAll('.切换按钮 button');
    buttons.forEach(button => {
        button.classList.toggle('选中', button.getAttribute('data-mode') === 存储模式);
    });

    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const 选择的模式 = this.getAttribute('data-mode');
            localStorage.setItem('搜索模式', 选择的模式);
            切换搜索模式(选择的模式);
            buttons.forEach(btn => btn.classList.toggle('选中', btn === this));
        });
    });
});

function 切换搜索模式(模式) {
    document.querySelector('.搜索模式-商标').style.display = (模式 === '商标') ? 'block' : 'none';
    document.querySelector('.搜索模式-申请号').style.display = (模式 === '申请号') ? 'block' : 'none';
    document.querySelector('.搜索模式-新增商标').style.display = (模式 === '新增商标') ? 'block' : 'none';
}

function 执行查询(表单ID, 路径, 请求体, 当前页 = 1) {
    event.preventDefault();
    const formData = new FormData(document.getElementById(表单ID));
    const jsonData = {
        ...请求体,
        '当前页': parseInt(formData.get('当前页')) || 1, // 从表单中获取当前页
        '每页数量': formData.get('每页数量')
    };

    fetch(路径, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
    })
        .then(response => response.json())
        .then(data => {
            updateUI(data);
            updatePaginationInfo(data.当前页, data.总页数);
        })
        .catch(error => console.error(`${表单ID} 请求错误:`, error));
}

function 执行商标查询() {
    执行查询('商标查询表单', API_URL.商标库查询, {
        '商标名': document.querySelector('input[name="商标名"]').value,
        '小类关键字': document.querySelector('input[name="小类关键字"]').value
    });
}

function 执行申请号查询() {
    执行查询('申请号查询表单', API_URL.申请号查询, {
        '申请号': document.querySelector('input[name="申请号"]').value
    });
}

// 高亮小类关键词的函数
function 高亮小类(小类文本, 正则表达式) {
    if (!正则表达式) return 小类文本; // 如果没有关键词则返回原文本
    return 小类文本.replace(正则表达式, '<span class="高亮">$1</span>'); // 使用 span 包裹高亮部分
}


// 更新 UI 的函数，加入修改按钮
function updateUI(data) {
    const resultContainer = document.getElementById('查询结果');
    resultContainer.innerHTML = '';

    // 显示查询结果数量
    document.querySelector('p').innerHTML = `当前查询共找到 <strong>${data.查询结果数量 || 0}</strong> 条记录`;

    // 判断查询结果是否为空
    if (!data.查询结果 || data.查询结果.length === 0) {
        resultContainer.innerHTML = '<p>未备案</p>';  // 显示“未备案”
        return;  // 退出函数，不再执行后续操作
    }

    const 小类关键词 = document.querySelector('input[name="小类关键字"]').value; // 获取输入的小类关键字
    const 高亮小类关键词 = 小类关键词 ? new RegExp(`(${小类关键词})`, 'gi') : null; // 创建正则表达式


    // 遍历查询结果，生成商标条目
    data.查询结果.forEach(商标 => {
        // 判断备案平台是否为空，若为空则显示“未备案”
        const 备案平台 = 商标[5] ? 商标[5] : '未备案';
        const 数据时间 = formatTimestamp(商标[6]);
        const 商标条目 = `
                <div class="商标条目" data-id="${商标[3]}">
                    <img class="商标图" src="${商标[0]}" alt="${商标[1]}商标图"/>
                    <div class="商标信息">
                        <h3>${商标[1]}</h3>
                        <p>申请人: ${商标[2]}</p>
                        <p>申请号: 
                            <span class="申请号">${商标[3].split('_')[0]}</span> 
                            <span class="品类">品类: ${商标[3].split('_')[1]}</span>
                            <span class="备案平台">备案平台: <span class="平台值">${备案平台}</span></span>
                        </p>
                        <span class="小类">${高亮小类(商标[4], 高亮小类关键词)}</span> <!-- 高亮小类 -->
                                <!-- 数据更新时间显示 -->
                           <p class="数据更新时间">数据更新时间: ${数据时间}</span></p>
    
                       
                        <button class="修改按钮">修改</button> <!-- 修改按钮 -->
                        <button class="更新按钮">更新数据</button><!-- 更新数据按钮 -->
                    </div>
                </div>`;
        resultContainer.innerHTML += 商标条目;
    });

    // 更新翻页信息
    document.querySelector('.结果信息 span').textContent = `第 ${data.当前页} 页 / 共 ${data.总页数} 页`;

    // 绑定修改按钮的点击事件
    document.querySelectorAll('.修改按钮').forEach(button => {
        button.addEventListener('click', function () {
            const 商标ID = this.closest('.商标条目').getAttribute('data-id');
            const 当前备案平台 = this.closest('.商标条目').querySelector('.平台值').textContent;

            // 打开修改弹窗并填充当前备案平台值
            openModifyModal(商标ID, 当前备案平台);
        });
    });


    // 绑定更新按钮的点击事件
    document.querySelectorAll('.更新按钮').forEach(button => {
        button.addEventListener('click', function () {
            const 商标ID = this.closest('.商标条目').getAttribute('data-id');
            const 当前备案平台 = this.closest('.商标条目').querySelector('.平台值').textContent;
            updateRecord(商标ID);

        });
    });
}

// 发送更新请求
function updateRecord(商标ID) {
    // 获取商标条目中的申请号
    const 商标条目 = document.querySelector(`.商标条目[data-id="${商标ID}"]`);
    const 申请号 = 商标条目.querySelector('.申请号').textContent.trim();  // 获取申请号

    // 如果申请号为空，则不发送请求
    if (!申请号) {
        显示错误信息('申请号为空');
        return;
    }

    // 发送 POST 请求到后端 API 更新商标信息
    fetch('/商标库/api/v1/更新商标信息', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            '申请号': 申请号, // 发送申请号给后端
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('后端返回数据:', data); // 输出后端返回的数据

            if (data.状态 === '成功') {
                显示成功信息('商标信息更新成功', data);
                // 调用更新后的重新加载函数
                reloadTrademarkData(商标ID);
            } else {
                显示错误信息('商标信息更新失败: ' + (data.信息 || '未知错误'));
            }
        })
        .catch(error => {
            console.error('请求失败:', error);
            显示错误信息('更新失败，请重试');
        });
}


function reloadTrademarkData(商标ID) {
    // 获取商标条目中的申请号
    const 商标条目 = document.querySelector(`.商标条目[data-id="${商标ID}"]`);
    const 申请号 = 商标条目.querySelector('.申请号').textContent.trim();  // 获取申请号

    // 如果申请号为空，则不发送请求
    if (!申请号) {
        显示错误信息('申请号为空');
        return;
    }

    // 发送 POST 请求到申请号查询接口
    fetch('/商标库/api/v1/申请号查询', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            '申请号': 申请号,  // 发送申请号给后端
            '当前页': 1,  // 你可以根据需求设置当前页
            '每页数量': 10,  // 每页数量
        })
    })
        .then(response => response.json())
        .then(data => {
            // 判断查询结果是否不为空
            if (data.查询结果 && data.查询结果.length > 0) {
                显示成功信息('商标信息更新成功', data);
                const 商标 = data.查询结果[0];  // 获取查询结果中的第一个商标

                // 获取商标条目的商标ID和备案平台
                const 备案平台 = 商标[5] || '未备案';  // 如果备案平台为空则显示'未备案'

                // 更新商标条目中的内容
                商标条目.querySelector('.申请号').textContent = 商标[3].split('_')[0];  // 更新申请号
                商标条目.querySelector('.平台值').textContent = 备案平台;  // 更新备案平台
                商标条目.querySelector('.小类').innerHTML = 商标[4];  // 高亮小类

                // 更新其他信息，如更新时间
                const 时间戳 = 商标[6];
                const formattedTime = formatTimestamp(时间戳);

                // 更新数据更新时间
                商标条目.querySelector('.数据更新时间').textContent = `数据更新时间: ${formattedTime}`;
            } else {
                显示错误信息('商标信息更新失败: ' + data.信息);
            }
        })
        .catch(error => {
            console.error('请求失败:', error);
            显示错误信息('更新失败，请重试');
        });
}


// 打开修改弹窗
function openModifyModal(商标ID, 当前备案平台) {
    const 平台列表 = ["京东", "淘宝", "拼多多", "抖音"];

    // 创建弹窗
    const modal = document.createElement('div');
    modal.classList.add('修改弹窗');
    modal.innerHTML = `
            <div class="修改弹窗内容">
                <h2>修改备案平台</h2>
                <div class="备案平台选择"></div>
                <button class="确认修改按钮">确认修改</button>
                <button class="关闭弹窗按钮">关闭</button>
            </div>
        `;

    document.body.appendChild(modal);

    const 备案平台选择区 = modal.querySelector('.备案平台选择');

    // 渲染平台按钮
    平台列表.forEach(平台 => {
        const 按钮 = document.createElement('button');
        按钮.textContent = 平台;
        按钮.classList.add('备案平台按钮');

        // 如果当前已备案，则默认高亮
        if (当前备案平台.includes(平台)) {
            按钮.classList.add('已选中');
        }

        // 绑定点击事件，切换选中状态
        按钮.addEventListener('click', () => {
            按钮.classList.toggle('已选中');
        });

        备案平台选择区.appendChild(按钮);
    });

    // 绑定关闭弹窗按钮
    modal.querySelector('.关闭弹窗按钮').addEventListener('click', () => {
        modal.remove();
    });

    // 绑定确认修改按钮
    modal.querySelector('.确认修改按钮').addEventListener('click', () => {
        // 获取所有选中的平台
        const 选中平台 = Array.from(modal.querySelectorAll('.备案平台按钮.已选中'))
            .map(按钮 => 按钮.textContent);

        // 如果没有选择任何平台，传递空字符串
        const 备案平台字符串 = 选中平台.length > 0 ? 选中平台.join(', ') : '';

        // 提交修改
        modify备案平台(商标ID, 备案平台字符串);

        // 关闭弹窗
        modal.remove();
    });
}


// 修改备案平台的请求
function modify备案平台(商标ID, 新备案平台) {
    // 如果备案平台为空（即未选择任何平台），则提交 null
    const requestBody = {
        申请号: 商标ID,
        备案平台: 新备案平台 ? 新备案平台 : null,// 如果 新备案平台 为空，则传递 null
        更新时间: new Date().toISOString()
    };

    // 发送 POST 请求
    fetch(API_URL.修改备案, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    })
        .then(response => response.json())  // 解析 JSON 响应
        .then(data => {
            if (data.状态 === '成功') {
                // 获取对应商标条目的 DOM 元素并更新备案平台值
                const 商标条目 = document.querySelector(`.商标条目[data-id="${商标ID}"]`);
                if (商标条目) {
                    商标条目.querySelector('.平台值').textContent = 新备案平台 || '未备案';  // 如果备案平台为空，显示'无'
                }
                显示成功信息('修改成功', data);
            } else {
                显示错误信息(`修改失败: ${data.信息}`);
            }
        })
        .catch(error => {
            console.error('请求出错:', error);
            显示错误信息('请求出错，请稍后重试！');
        });
}


function updatePaginationInfo(currentPage, totalPages) {
    document.querySelector('.翻页按钮 span').innerText = `第 ${currentPage} 页 / 共 ${totalPages} 页`;
    document.querySelector('.上一页按钮').disabled = currentPage === 1;
    document.querySelector('.下一页按钮').disabled = currentPage === totalPages;
}

function changePage(方向) {
    const 当前页 = parseInt(document.querySelector('input[name="当前页"]').value);
    const 每页数量 = parseInt(document.querySelector('input[name="每页数量"]').value);
    const 新页 = 当前页 + 方向;

    // 检查新页数是否合理
    if (新页 < 1) return; // 不允许小于 1
    // 假设你有总页数的变量
    const 总页数 = parseInt(document.querySelector('.结果信息 span').textContent.split('/')[1]);

    if (新页 > 总页数) return; // 不允许超过总页数

    // 更新当前页值
    document.querySelector('input[name="当前页"]').value = 新页;

    // 获取存储模式，默认商标
    const 存储模式 = localStorage.getItem('搜索模式') || '商标';

    // 根据存储模式执行相应的查询
    if (存储模式 === '商标') {
        执行商标查询();
    } else if (存储模式 === '申请号') {
        执行申请号查询();
    }
}

function 重置页码(查询类型) {
    // 重置当前页为1
    document.querySelector('input[name="当前页"]').value = 1;
    if (查询类型 === '商标') {
        执行商标查询(); // 调用商标查询
    } else if (查询类型 === '申请号') {
        执行申请号查询(); // 调用申请号查询
    }
}

function 执行新增商标() {
    // 获取申请号的值
    const 申请号 = document.querySelector('input[name="申请号-新增"]').value.trim();
    // 获取用户名的值
    const 用户名 = document.querySelector('input[name="用户名"]').value.trim();

    // 检查申请号是否为空
    if (!申请号) {
        显示错误信息("申请号不能为空！");
        return;
    }

    // 检查用户名是否为空
    if (!用户名) {
        显示错误信息("用户名不能为空！");
        return;
    }

    // 将用户名存储在 Cookie 中，无论请求是否成功
    document.cookie = `用户名=${用户名}; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/`;

    // 创建并发送请求
    fetch(API_URL.插入商标, {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: 申请号,
    })
        .then(response => {
            if (!response.ok) {
                if (response.status === 409) {
                    return response.json();
                }
                throw new Error(`HTTP 错误状态: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.状态 === "成功") {
                显示成功信息(data.信息, data); // 显示成功信息并返回数据
            } else {
                显示错误信息(`请求失败: ${data.信息}`);
            }
        })
        .catch(error => {
            console.error('请求出错:', error);
            显示错误信息('请求出错，请稍后重试！');
        });
}


// 显示错误信息
function 显示错误信息(信息) {
    const 错误标签 = document.createElement('div');
    错误标签.textContent = 信息;
    错误标签.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: rgba(255, 0, 0, 0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            z-index: 1000;
            font-size: 14px;
        `;
    document.body.appendChild(错误标签);

    // 3 秒后自动销毁
    setTimeout(() => {
        错误标签.remove();
    }, 3000);
}

// 显示成功信息（样式调整）
function 显示成功信息(信息, 返回值) {
    const 成功标签 = document.createElement('div');
    成功标签.textContent = `${信息} (${JSON.stringify(返回值)})`;
    成功标签.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: rgba(0, 128, 0, 0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            z-index: 1000;
            font-size: 14px;
        `;
    document.body.appendChild(成功标签);

    // 3 秒后自动销毁
    setTimeout(() => {
        成功标签.remove();
    }, 3000);
}

// 从 Cookie 中获取指定键的值
function 获取Cookie值(键名) {
    const 匹配项 = document.cookie.match(new RegExp(`(?:^|; )${键名}=([^;]*)`));
    return 匹配项 ? decodeURIComponent(匹配项[1]) : '';
}

// 页面加载时自动填充用户名
window.addEventListener('DOMContentLoaded', () => {
    const 用户名输入框 = document.querySelector('input[name="用户名"]');
    if (用户名输入框) {
        const 用户名 = 获取Cookie值('用户名'); // 从 Cookie 获取用户名
        if (用户名) {
            用户名输入框.value = 用户名; // 填充到输入框中
        }
    }
});

// 格式化时间戳为指定格式：yyyy-MM-dd HH:mm:ss
function formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);  // 转换为毫秒
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // 月份从 0 开始，所以加 1
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}