class 产品查询 {
    constructor() {
        this.currentPage = 1;  // 当前页
        this.productsPerPage = 30;  // 每页产品数量
        this.isSearching = false;  // 防止连续点击查询按钮
        this.totalPages = 1;  // 总页数初始化
    }

    // 执行产品查询
    搜索产品(isQuery = true) {
        if (this.isSearching) return;  // 防止重复查询
        this.isSearching = true;  // 标记为正在查询

        console.log("开始查询...");

        // 如果是查询操作，重置页码
        if (isQuery) {
            this.重置页码();  // 重置页码时已经调用了搜索，所以这里不需要重复调用
        }

        console.log("正在发送请求...");
        const 品类 = document.getElementById('品类').value;
        const 品名 = document.getElementById('品名').value;

        fetch('/产品库查询', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                品类: 品类,
                品名: 品名,
                当前页: this.currentPage,
                每页数量: this.productsPerPage
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log("返回的数据:", data);  // 调试查看返回数据
                this.renderProducts(data);  // 渲染查询结果
                this.isSearching = false;  // 查询结束，恢复标记
            })
            .catch(error => {
                console.error('Error:', error);
                this.isSearching = false;  // 出现错误时恢复标记
            });
    }

    // 渲染产品数据
// 渲染产品数据
renderProducts(data) {
    const container = document.getElementById('查询结果');
    container.innerHTML = '';  // 清空之前的内容

    // 遍历查询结果并渲染
    data.查询结果.forEach(product => {
        const productDiv = document.createElement('div');
        productDiv.classList.add('查询结果卡片');  // 添加卡片样式类

        // 提取返回数据中的字段，若没有则使用默认值
        const 品类 = product[0] || '未知品类';
        const 品名 = product[1] || '未知产品';
        const 型号 = product[2] || '无型号';
        const 产品图片 = product[3] || 'default-image.jpg';  // 使用默认图片
        const 产品链接 = product[4] || '#';  // 使用空链接作为默认

        const cardHTML = `
            <div class="查询结果卡片内容">
                <!-- 点击图片放大 -->
                <img src="${产品图片}" alt="${品名}" class="产品图" onclick="点击图片(event, '${产品图片}')">
                <div class="产品信息">
                    <h3 class="品名">${品名}</h3>
                    <p class="品类">${品类}</p>
                    <p class="型号">${型号}</p>
                </div>
            </div>
            <div class="卡片底部按钮">
                <!-- 详情链接，点击跳转 -->
                <a href="${产品链接}" class="卡片按钮" target="_blank">查看详情</a>
            </div>
        `;
        productDiv.innerHTML = cardHTML;
        container.appendChild(productDiv);
    });

    // 更新当前页和总页数
    this.totalPages = data.总页数;  // 获取总页数
    document.getElementById('当前页').innerText = data.当前页;
    document.getElementById('总页数').innerText = this.totalPages;

    // 启用/禁用翻页按钮
    this.togglePaginationButtons(data.当前页, this.totalPages);
}

    // 控制翻页按钮的启用和禁用
// 控制翻页按钮的启用和禁用
    togglePaginationButtons(当前页, 总页数) {
        const prevButton = document.querySelector('.翻页按钮 .上一页按钮');
        const nextButton = document.querySelector('.翻页按钮 .下一页按钮');

        console.log('prevButton:', prevButton);
        console.log('nextButton:', nextButton);
        console.log('当前页:', 当前页, '总页数:', 总页数);

        if (prevButton && nextButton) {
            // 如果是第一页，禁用上一页按钮
            prevButton.disabled = 当前页 <= 1;
            // 如果是最后一页，禁用下一页按钮
            nextButton.disabled = 当前页 >= 总页数;
        } else {
            console.error('未找到翻页按钮');
        }
    }


// 改变页码（翻页）
    changePage(direction) {
        const newPage = this.currentPage + direction;
        // 确保页数不超出范围
        if (newPage >= 1 && newPage <= this.totalPages) {
            this.currentPage = newPage;  // 更新当前页
            console.log('当前页:', this.currentPage);  // 调试信息，确保页码正确
            this.搜索产品(false);  // 改变页码后重新查询，传入 false 表示不要重置页码
        }
    }


    // 重置页码函数
    重置页码() {
        console.log("重置页码函数被调用");

        // 打印当前页和总页数
        console.log("当前页:", this.currentPage);
        console.log("总页数:", this.totalPages);

        this.currentPage = 1;  // 重置当前页为 1
        console.log("更新当前页为:", this.currentPage);

        const 当前页元素 = document.getElementById('当前页');
        if (当前页元素) {
            当前页元素.innerText = this.currentPage;
        } else {
            console.error('未找到当前页元素');
        }

        // 更新翻页按钮状态
        this.togglePaginationButtons(this.currentPage, this.totalPages);

        console.log("页码重置完成");
    }
}

// 创建产品查询对象
const 产品查询实例 = new 产品查询();

// 绑定查询按钮事件
document.querySelector('button').addEventListener('click', () => {
    产品查询实例.搜索产品();  // 调用搜索产品方法
});

// 处理点击图片事件
function 点击图片(event, 图片链接) {
    event.preventDefault(); // 阻止默认的链接跳转
    放大图片(图片链接);    // 调用放大图片的函数
}

// 放大图片函数
function 放大图片(图片链接) {
    // 获取放大容器元素
    const 放大容器 = document.getElementById('放大容器');
    const 放大图片 = document.getElementById('放大图片');

    // 设置放大图片的源
    放大图片.src = 图片链接;

    // 显示放大容器
    放大容器.style.display = 'flex'; // 弹出窗口类型的容器，使用 flex 居中显示
}

// 关闭放大图
function 关闭放大图() {
    const 放大容器 = document.getElementById('放大容器');

    // 隐藏放大容器
    放大容器.style.display = 'none';
}