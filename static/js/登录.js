
// 安全登录函数
async function secureLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const nextPage = document.getElementById('next-page').value;
    
    if (!username || !password) {
        showError('请输入用户名和密码');
        return false;
    }
    
    try {
        // 使用MD5直接对密码进行哈希处理
        const passwordHash = CryptoJS.MD5(password).toString();
        
        // 发送登录请求
        const loginResponse = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password_hash: passwordHash,  // 发送哈希后的密码而非明文
                next: nextPage
            })
        });
        
        const loginResult = await loginResponse.json();
        
        if (loginResult.success) {
            // 登录成功，重定向到指定页面
            window.location.href = loginResult.redirect || '/';
        } else {
            // 登录失败，显示错误信息
            showError(loginResult.message || '登录失败，请检查用户名和密码');
        }
    } catch (error) {
        console.error('登录过程中发生错误:', error);
        showError('登录过程中发生错误，请稍后重试');
    }
    
    return false;
}

// 显示错误信息
function showError(message) {
    const errorDiv = document.getElementById('login-error');
    const errorMessage = document.getElementById('error-message');
    
    errorMessage.textContent = message;
    errorDiv.style.display = 'block';
    
    // 5秒后自动隐藏错误信息
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 设置表单提交事件
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', secureLogin);
    }
    
    // 定时检测开发者工具
    setInterval(detectDevTools, 1000); // 每秒检测一次
}); 