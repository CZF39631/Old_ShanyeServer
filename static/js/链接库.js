// 常量定义
const API_URL = {
    上传: '/链接库/api/v1/上传',
    查询: '/链接库/api/v1/查询',
    查询客户: '/链接库/api/v1/ID查询'
};

// DOM 元素获取
const 上传区域 = document.getElementById('uploadDropArea');
const 文件输入 = document.getElementById('fileInput');
const 上传按钮 = document.getElementById('uploadButton');
const 上传文件名 = document.getElementById('uploadFileName');
const 上传信息 = document.getElementById('上传信息');

const 查询区域 = document.getElementById('queryDropArea');
const 查询文件输入 = document.getElementById('queryFileInput');
const 查询按钮 = document.getElementById('queryButton');
const 查询文件名 = document.getElementById('queryFileName');
const 查询信息 = document.getElementById('查询信息');
const 下载按钮 = document.getElementById('downloadButton');

const 查询客户按钮 = document.getElementById('queryCustomerButton');
const 链接ID输入 = document.getElementById('linkIdInput');
const 客户名 = document.getElementById('customerName');

// 函数定义

// 添加拖拽事件
const 添加拖拽事件 = (区域, 文件输入框, 文件名显示区域) => {
    // 点击上传区域时，触发文件输入框点击
    区域.addEventListener('click', () => {
        文件输入框.click();  // 触发文件选择
    });

    // 拖拽到区域时
    区域.addEventListener('dragover', (e) => {
        e.preventDefault();
        区域.classList.add('hover');
    });

    // 拖拽离开区域时
    区域.addEventListener('dragleave', () => {
        区域.classList.remove('hover');
    });

    // 文件放入区域时
    区域.addEventListener('drop', (e) => {
        e.preventDefault();
        区域.classList.remove('hover');
        if (e.dataTransfer.files.length) {
            文件输入框.files = e.dataTransfer.files;  // 获取文件
            文件名显示区域.textContent = e.dataTransfer.files[0].name;  // 显示文件名
        }
    });

    // 文件选择后更新显示
    文件输入框.addEventListener('change', () => {
        if (文件输入框.files.length > 0) {
            文件名显示区域.textContent = 文件输入框.files[0].name;  // 显示文件名
        }
    });
};

// 文件上传功能
const 文件上传 = () => {
    const 文件 = 文件输入.files[0];

    // 校验文件名格式
    const 客户名 = 文件.name.match(/^(.*?)[-_+].*链接库/);
    if (!客户名) {
        上传信息.textContent = '文件名格式不正确，请使用“客户名+链接库.xlsx”格式的文件';
        上传信息.className = 'status-message status-error';
        return;
    }

    // 提取客户名
    const 客户名提取 = 客户名[1];  // 客户名是第一个捕获组

    // 创建表单数据
    const 表单数据 = new FormData();
    表单数据.append('file', 文件);

    // 显示“请等待”信息
    上传信息.textContent = '请等待，文件上传中...';
    上传信息.className = 'status-message status-pending';

    // 发起文件上传请求
    fetch(API_URL.上传, {
        method: 'POST',
        body: 表单数据
    })
    .then(response => response.json())
    .then(data => {
        const 当前时间 = new Date().toLocaleString();

        // 判断返回的message字段，确认上传是否成功
        if (data.success_count > 0) {
            上传信息.textContent = `文件上传成功！上传时间: ${当前时间}，成功上传 ${data.success_count} 条记录`;
            上传信息.className = 'status-message status-success';
        } else {
            上传信息.textContent = `上传失败：${data.message || '未知错误'}。请重试。`;
            上传信息.className = 'status-message status-error';
        }
    })
    .catch(error => {
        console.error('上传失败:', error);
        上传信息.textContent = `上传失败，失败记录为 ${data.failed_records}。`;
        上传信息.className = 'status-message status-error';
    });
};

// 查询数据功能
const 数据查询 = () => {
    const 表单数据 = new FormData();
    表单数据.append('file', 查询文件输入.files[0]);

    fetch(API_URL.查询, {
        method: 'POST',
        body: 表单数据
    })
    .then(response => response.json())
    .then(data => {
        const 当前时间 = new Date().toLocaleString();
        if (data.data) {
            window.查询结果数据 = data.data;  // 保存查询结果
            console.log(data);  // 打印查询返回的数据
            查询信息.textContent = `查询成功！查询时间: ${当前时间}，结果 ${data.data.length} 条`;
            查询信息.className = 'status-message status-success';
            下载按钮.style.display = 'inline-block'; // 显示下载按钮
        } else {
            查询信息.textContent = '查询无结果，请检查文件内容。';
            查询信息.className = 'status-message status-error';
        }
    })
    .catch(error => {
        console.error('查询失败:', error);
        查询信息.textContent = '查询失败，请重试。';
        查询信息.className = 'status-message status-error';
    });
};

// 下载查询结果功能
const 下载查询结果 = () => {
    // 检查查询结果数据是否存在且非空
    if (!window.查询结果数据 || window.查询结果数据.length === 0) {
        alert('请先进行查询！');
        return;
    }

    // 打印原始数据，检查数据结构
    console.log('原始查询结果数据：', window.查询结果数据);

    const 表头 = ["链接ID", "侵权情况",];

    // 使用 map 重新映射字段，确保字段正确处理
    const 数据_带表头 = [
        表头,
        ...window.查询结果数据.map((row, index) => {
            if (Array.isArray(row)) {
                return [
                    String(row[0]) ?? '',  // 确保链接ID是文本类型
                    row[1] ?? '',  // 侵权情况
                ];
            } else {
                console.warn(`第 ${index + 1} 行数据不是一个数组：`, row);
                return Array(9).fill('');  // 如果不是数组，填充空字符串
            }
        })
    ];

    // 打印映射后的数据，确认映射是否正确
    console.log('映射后的查询结果数据：', 数据_带表头);

    const 工作表 = XLSX.utils.aoa_to_sheet(数据_带表头);
    const 工作簿 = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(工作簿, 工作表, '查询结果');
    XLSX.writeFile(工作簿, '查询结果.xlsx');
};

// 根据链接ID查询客户名功能
const 查询客户名 = () => {
    const 链接ID = 链接ID输入.value.trim();
    if (!链接ID) {
        客户名.textContent = '请输入链接ID。';
        return;
    }

    fetch(API_URL.查询客户, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ link_id: 链接ID })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('网络响应不是 OK');
        }
        return response.json();
    })
    .then(data => {
        客户名.textContent = data.customer_name ? `客户名: ${data.customer_name}, 是否侵权: ${data.类别}` : '找不到链接记录。';
    })
    .catch(error => {
        console.error('查询失败:', error);
        客户名.textContent = '查询失败，请重试。';
    });
};

// 事件绑定

// 上传按钮点击事件
上传按钮.addEventListener('click', 文件上传);

// 查询按钮点击事件
查询按钮.addEventListener('click', 数据查询);

// 下载按钮点击事件
下载按钮.addEventListener('click', 下载查询结果);

// 查询客户按钮点击事件
查询客户按钮.addEventListener('click', 查询客户名);

// 绑定拖拽事件到上传和查询区域
添加拖拽事件(上传区域, 文件输入, 上传文件名);
添加拖拽事件(查询区域, 查询文件输入, 查询文件名);
