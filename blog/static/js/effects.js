/**
 * 星光背景效果
 * 在页面加载时创建动态的星星效果
 */
document.addEventListener('DOMContentLoaded', function() {
    createStars();
});

/**
 * 创建星星元素并添加到页面
 * 每个星星有随机位置、大小和动画持续时间
 */
function createStars() {
    const body = document.body;
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    const starCount = 50;
    
    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        
        // 随机位置
        star.style.left = `${Math.random() * screenWidth}px`;
        star.style.top = `${Math.random() * screenHeight}px`;
        
        // 随机大小
        const size = Math.random() * 2;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        
        // 随机动画持续时间
        const duration = 2 + Math.random() * 3;
        star.style.setProperty('--duration', `${duration}s`);
        
        // 随机延迟
        star.style.animationDelay = `${Math.random() * 3}s`;
        
        body.appendChild(star);
    }
}

/**
 * 页面大小变化时重新计算星星位置
 */
window.addEventListener('resize', function() {
    // 移除现有星星
    document.querySelectorAll('.star').forEach(star => star.remove());
    // 重新创建星星
    createStars();
}); 