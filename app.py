import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Pixel Dungeon Crawler RPG",
    page_icon="⚔️",
    layout="centered"
)

st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #f1c40f;
        font-family: 'Courier New', Courier, monospace;
    }
    .instructions {
        text-align: center;
        color: #ccc;
        font-size: 14px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>⚔️ PIXEL DUNGEON CRAWLER RPG ⚔️</h1>", unsafe_allow_html=True)
st.markdown("<div class='instructions'>Dùng phím <b>W, A, S, D</b> hoặc <b>Phím Mũi Tên</b> để di chuyển. Tiêu diệt quái vật, mở rương và tìm lối xuống tầng hầm tiếp theo!</div>", unsafe_allow_html=True)

# Mã HTML/JS giả lập đồ họa Pixel Art chi tiết
game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Detailed Pixel Dungeon</title>
    <style>
        body {
            background-color: #0b0b0e;
            color: #ffffff;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 10px;
            overflow: hidden;
        }
        #game-container {
            border: 4px solid #3d2817;
            background-color: #121016;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.9), inset 0 0 20px rgba(0,0,0,0.8);
            position: relative;
        }
        canvas {
            display: block;
            image-rendering: pixelated;
        }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="gameCanvas" width="600" height="400"></canvas>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const TILE_SIZE = 40;
        const COLS = 15;
        const ROWS = 10;

        let player = {
            x: 1,
            y: 1,
            hp: 80,
            maxHp: 100,
            lvl: 3,
            score: 2450,
            floor: 2,
            keys: 1
        };

        // 0: Sàn gạch, 1: Tường đá rêu phong, 2: Cầu thang xuống, 3: Rương báu
        let map = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,3,0,1,0,0,2,1],
            [1,0,1,0,1,0,1,1,0,0,1,0,1,0,1],
            [1,0,1,0,0,0,0,1,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,0,1,1,1,0,1,1,0,1],
            [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
            [1,1,1,0,1,1,1,1,0,1,1,1,1,0,1],
            [1,3,0,0,0,0,0,1,0,0,0,0,3,0,1],
            [1,0,1,1,1,1,0,0,0,1,1,1,1,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ];

        let monsters = [
            { x: 12, y: 5, hp: 40, maxHp: 40, color: '#e74c3c', type: 'slime' },
            { x: 6, y: 3, hp: 30, maxHp: 30, color: '#9b59b6', type: 'bat' },
            { x: 3, y: 7, hp: 50, maxHp: 50, color: '#e74c3c', type: 'slime' }
        ];

        // Xử lý di chuyển bàn phím
        window.addEventListener('keydown', e => {
            let newX = player.x;
            let newY = player.y;

            if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') newY--;
            if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') newY++;
            if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') newX--;
            if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') newX++;

            if (newY >= 0 && newY < ROWS && newX >= 0 && newX < COLS) {
                let tile = map[newY][newX];

                // Kiểm tra va chạm tường
                if (tile !== 1) {
                    // Kiểm tra quái vật
                    let mIndex = monsters.findIndex(m => m.x === newX && m.y === newY);
                    if (mIndex !== -1) {
                        // Tấn công quái
                        monsters[mIndex].hp -= 25;
                        player.score += 50;
                        if (monsters[mIndex].hp <= 0) {
                            monsters.splice(mIndex, 1);
                        }
                    } else if (tile === 3) {
                        // Mở rương
                        player.score += 300;
                        player.keys += 1;
                        map[newY][newX] = 0; // Rương biến mất thành sàn
                    } else if (tile === 2) {
                        // Xuống tầng mới
                        player.floor++;
                        player.score += 500;
                        player.x = 1;
                        player.y = 1;
                        alert("Chúc mừng! Bạn đã xuống Tầng " + player.floor);
                        return;
                    } else {
                        player.x = newX;
                        player.y = newY;
                    }
                }
            }

            // Quái tấn công lại người chơi nếu đứng gần
            monsters.forEach(m => {
                if (Math.abs(m.x - player.x) + Math.abs(m.y - player.y) === 1) {
                    player.hp -= 10;
                    if (player.hp <= 0) {
                        alert("Game Over! Điểm số của bạn: " + player.score);
                        player.hp = 100;
                        player.score = 0;
                        player.floor = 1;
                        player.x = 1;
                        player.y = 1;
                    }
                }
            });

            drawGame();
        });

        // Hàm vẽ Pixel Art chi tiết mô phỏng phong cách RPG cổ điển
        function drawGame() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ Map (Hầm ngục)
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    let x = c * TILE_SIZE;
                    let y = r * TILE_SIZE;

                    if (map[r][c] === 1) {
                        // Tường đá rêu phong
                        ctx.fillStyle = '#2c223b';
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.fillStyle = '#3e3154';
                        ctx.fillRect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4);
                        // Họa tiết rêu
                        ctx.fillStyle = '#27ae60';
                        ctx.fillRect(x + 4, y + 25, 6, 10);
                    } else {
                        // Sàn đá lát
                        ctx.fillStyle = '#1b1726';
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.strokeStyle = '#252033';
                        ctx.strokeRect(x, y, TILE_SIZE, TILE_SIZE);
                    }

                    // Cầu thang xuống tầng (2)
                    if (map[r][c] === 2) {
                        ctx.fillStyle = '#f1c40f';
                        ctx.fillRect(x + 5, y + 5, TILE_SIZE - 10, TILE_SIZE - 10);
                        ctx.fillStyle = '#d4ac0d';
                        ctx.fillRect(x + 10, y + 10, TILE_SIZE - 20, TILE_SIZE - 20);
                    }

                    // Hòm kho báu (3)
                    if (map[r][c] === 3) {
                        ctx.fillStyle = '#d35400';
                        ctx.fillRect(x + 8, y + 12, 24, 18);
                        ctx.fillStyle = '#f39c12';
                        ctx.fillRect(x + 16, y + 18, 8, 6); // Khóa rương
                    }
                }
            }

            // 2. Vẽ Quái vật (Slime gai đỏ & Dơi)
            monsters.forEach(m => {
                let mx = m.x * TILE_SIZE;
                let my = m.y * TILE_SIZE;
                if (m.type === 'slime') {
                    // Thân Slime đỏ
                    ctx.fillStyle = '#e74c3c';
                    ctx.beginPath();
                    ctx.arc(mx + 20, my + 25, 12, Math.PI, 0, false);
                    ctx.fill();
                    // Gai slime
                    ctx.fillStyle = '#c0392b';
                    ctx.fillRect(mx + 16, my + 8, 8, 8);
                    // Mắt quái
                    ctx.fillStyle = '#fff';
                    ctx.fillRect(mx + 14, my + 18, 4, 4);
                    ctx.fillRect(mx + 22, my + 18, 4, 4);
                } else {
                    // Dơi tím
                    ctx.fillStyle = '#9b59b6';
                    ctx.fillRect(mx + 10, my + 15, 20, 10);
                }
            });

            // 3. Vẽ Nhân vật chính (Hiệp sĩ áo choàng xanh)
            let px = player.x * TILE_SIZE;
            let py = player.y * TILE_SIZE;
            
            // Áo choàng xanh
            ctx.fillStyle = '#2980b9';
            ctx.fillRect(px + 8, py + 12, 24, 20);
            // Giáp sắt nhân vật
            ctx.fillStyle = '#bdc3c7';
            ctx.fillRect(px + 12, py + 8, 16, 16);
            // Mũ & Tóc
            ctx.fillStyle = '#8e44ad';
            ctx.fillRect(px + 12, py + 4, 16, 8);
            // Kiếm sáng lấp lánh trên tay
            ctx.fillStyle = '#ecf0f1';
            ctx.fillRect(px + 28, py + 14, 8, 4);
            ctx.fillStyle = '#f1c40f';
            ctx.fillRect(px + 32, py + 12, 4, 8);

            // 4. Vẽ Khung UI / Giao diện HUD (giống hình minh họa)
            // Khung nền HUD góc trên trái
            ctx.fillStyle = 'rgba(15, 15, 20, 0.85)';
            ctx.fillRect(10, 10, 210, 85);
            ctx.strokeStyle = '#555';
            ctx.strokeRect(10, 10, 210, 85);

            // Thanh HP Bar
            ctx.fillStyle = '#c0392b';
            ctx.fillRect(20, 20, 140, 16);
            ctx.fillStyle = '#2ecc71';
            let hpWidth = (player.hp / player.maxHp) * 140;
            ctx.fillRect(20, 20, hpWidth, 16);
            
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 11px "Courier New"';
            ctx.fillText(`HP: ${player.hp}/${player.maxHp}`, 26, 32);

            // Text thông số (LVL, SCORE, FLOOR, KEYS)
            ctx.fillStyle = '#f1c40f';
            ctx.fillText(`LVL: ${player.lvl}`, 20, 52);
            ctx.fillText(`SCORE: ${player.score}`, 20, 72);
            
            ctx.fillStyle = '#3498db';
            ctx.fillText(`FLOOR: ${player.floor}F`, 120, 52);
            ctx.fillStyle = '#e67e22';
            ctx.fillText(`KEYS: ${player.keys}`, 120, 72);
        }

        drawGame();
    </script>
</body>
</html>
"""

components.html(game_html, height=450)

