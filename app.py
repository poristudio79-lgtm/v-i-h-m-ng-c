import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Multi-Floor Pixel Dungeon Crawler",
    page_icon="🗡️",
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

st.markdown("<h1 class='main-title'>🗡️ PIXEL DUNGEON CRAWLER: MULTI-FLOOR ⚔️</h1>", unsafe_allow_html=True)
st.markdown("<div class='instructions'>Dùng phím <b>W, A, S, D</b> hoặc <b>Phím Mũi Tên</b> để di chuyển. Mỗi tầng hầm sẽ có bản đồ mới và loại quái vật nguy hiểm hơn!</div>", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Dynamic Pixel Dungeon</title>
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
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.9);
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
            hp: 90,
            maxHp: 100,
            lvl: 1,
            score: 0,
            floor: 1,
            keys: 0
        };

        let currentMap = [];
        let monsters = [];
        let exitCoord = { x: 13, y: 8 };

        // Định nghĩa các bản đồ (Map) và Quái vật theo từng tầng
        function loadFloor(floorNum) {
            player.x = 1;
            player.y = 1;

            if (floorNum === 1) {
                // Tầng 1: Cấu trúc cơ bản, quái yếu (Slime & Dơi)
                currentMap = [
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
                exitCoord = { x: 13, y: 1 };
                monsters = [
                    { x: 12, y: 5, hp: 25, maxHp: 25, type: 'slime', name: 'Slime Nhỏ' },
                    { x: 6, y: 3, hp: 20, maxHp: 20, type: 'bat', name: 'Dơi Đói' },
                    { x: 3, y: 7, hp: 30, maxHp: 30, type: 'slime', name: 'Slime Xanh' }
                ];
            } 
            else if (floorNum === 2) {
                // Tầng 2: Mê cung rộng hơn, quái mạnh hơn (Goblin & Nhện độc)
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,1,0,0,0,1,0,0,0,3,0,0,0,1],
                    [1,0,1,1,1,0,1,0,1,1,1,1,1,0,1],
                    [1,0,0,0,1,0,0,0,1,0,0,0,1,0,1],
                    [1,1,1,0,1,1,1,0,1,0,1,0,1,0,1],
                    [1,3,0,0,0,0,1,0,0,0,1,0,0,2,1],
                    [1,0,1,1,1,0,1,1,1,1,1,1,1,0,1],
                    [1,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
                    [1,1,1,0,3,1,1,1,1,1,1,0,3,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 5 };
                monsters = [
                    { x: 7, y: 3, hp: 45, maxHp: 45, type: 'goblin', name: 'Goblin Trộm' },
                    { x: 3, y: 5, hp: 40, maxHp: 40, type: 'spider', name: 'Nhện Độc' },
                    { x: 11, y: 7, hp: 50, maxHp: 50, type: 'goblin', name: 'Goblin Chiến Binh' }
                ];
            } 
            else {
                // Tầng 3+: Tầng hầm tối tăm, quái trùm (Quỷ đá / Golem)
                currentMap = [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,0,0,1,3,0,0,0,0,1,2,1],
                    [1,0,1,1,1,0,1,1,1,0,1,0,1,0,1],
                    [1,0,1,3,1,0,0,0,1,0,1,0,1,0,1],
                    [1,0,1,0,1,1,1,0,1,0,1,1,1,0,1],
                    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
                    [1,1,1,1,1,0,1,1,1,1,1,0,1,1,1],
                    [1,0,0,0,1,0,0,0,3,0,1,0,0,3,1],
                    [1,0,1,0,1,1,1,1,1,0,1,1,1,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ];
                exitCoord = { x: 13, y: 1 };
                monsters = [
                    { x: 7, y: 4, hp: 80, maxHp: 80, type: 'golem', name: 'Golem Hầm Ngục' },
                    { x: 3, y: 1, hp: 60, maxHp: 60, type: 'demon', name: 'Quỷ Lửa' },
                    { x: 13, y: 7, hp: 70, maxHp: 70, type: 'demon', name: 'Quỷ Bóng Tối' }
                ];
            }
            // Đặt ô cầu thang xuống tầng trên bản đồ
            currentMap[exitCoord.y][exitCoord.x] = 2;
        }

        // Khởi động tầng đầu tiên
        loadFloor(1);

        // Xử lý bàn phím di chuyển
        window.addEventListener('keydown', e => {
            let newX = player.x;
            let newY = player.y;

            if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') newY--;
            if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') newY++;
            if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') newX--;
            if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') newX++;

            if (newY >= 0 && newY < ROWS && newX >= 0 && newX < COLS) {
                let tile = currentMap[newY][newX];

                if (tile !== 1) { // Không phải tường
                    let mIndex = monsters.findIndex(m => m.x === newX && m.y === newY);
                    if (mIndex !== -1) {
                        // Tấn công quái
                        let dmg = 25 + (player.lvl * 5);
                        monsters[mIndex].hp -= dmg;
                        player.score += 100;
                        if (monsters[mIndex].hp <= 0) {
                            monsters.splice(mIndex, 1);
                            player.score += 200;
                            // Lên cấp mỗi khi diệt được nhiều quái
                            if (player.score >= player.lvl * 600) {
                                player.lvl++;
                                player.maxHp += 20;
                                player.hp = player.maxHp;
                                alert("🎉 Chúc mừng! Bạn đã thăng lên Level " + player.lvl);
                            }
                        }
                    } else if (tile === 3) {
                        // Mở rương kho báu
                        player.score += 400;
                        player.keys += 1;
                        player.hp = Math.min(player.maxHp, player.hp + 30); // Hồi máu từ rương
                        currentMap[newY][newX] = 0; // Biến rương thành sàn trống
                    } else if (tile === 2) {
                        // Xuống tầng hầm tiếp theo
                        player.floor++;
                        player.score += 800;
                        alert("⚡ Đã xuống Tầng " + player.floor + "! Môi trường và quái vật mới xuất hiện.");
                        loadFloor(player.floor);
                        drawGame();
                        return;
                    } else {
                        player.x = newX;
                        player.y = newY;
                    }
                }
            }

            // Quái phản công người chơi nếu đứng cạnh
            monsters.forEach(m => {
                if (Math.abs(m.x - player.x) + Math.abs(m.y - player.y) === 1) {
                    let monsterDmg = 10 + (player.floor * 5);
                    player.hp -= monsterDmg;
                    if (player.hp <= 0) {
                        alert("💀 Game Over! Bạn đã tử trận ở Tầng " + player.floor + ". Điểm số: " + player.score);
                        player.hp = 100;
                        player.maxHp = 100;
                        player.score = 0;
                        player.floor = 1;
                        player.lvl = 1;
                        player.keys = 0;
                        loadFloor(1);
                    }
                }
            });

            drawGame();
        });

        // Vẽ đồ họa pixel art chi tiết
        function drawGame() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ Map theo tầng hiện tại
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    let x = c * TILE_SIZE;
                    let y = r * TILE_SIZE;

                    if (currentMap[r][c] === 1) {
                        // Tường đá
                        ctx.fillStyle = player.floor === 2 ? '#22313f' : (player.floor >= 3 ? '#4a1515' : '#2c223b');
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.fillStyle = '#3e3154';
                        ctx.fillRect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4);
                    } else {
                        // Sàn đá
                        ctx.fillStyle = '#1b1726';
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.strokeStyle = '#252033';
                        ctx.strokeRect(x, y, TILE_SIZE, TILE_SIZE);
                    }

                    // Cầu thang xuống tầng (2)
                    if (currentMap[r][c] === 2) {
                        ctx.fillStyle = '#f1c40f';
                        ctx.fillRect(x + 4, y + 4, TILE_SIZE - 8, TILE_SIZE - 8);
                        ctx.fillStyle = '#d4ac0d';
                        ctx.fillRect(x + 10, y + 10, TILE_SIZE - 20, TILE_SIZE - 20);
                    }

                    // Hòm kho báu (3)
                    if (currentMap[r][c] === 3) {
                        ctx.fillStyle = '#d35400';
                        ctx.fillRect(x + 8, y + 12, 24, 18);
                        ctx.fillStyle = '#f39c12';
                        ctx.fillRect(x + 16, y + 18, 8, 6);
                    }
                }
            }

            // 2. Vẽ Quái vật đặc thù của tầng
            monsters.forEach(m => {
                let mx = m.x * TILE_SIZE;
                let my = m.y * TILE_SIZE;

                if (m.type === 'slime') {
                    ctx.fillStyle = '#e74c3c';
                    ctx.beginPath();
                    ctx.arc(mx + 20, my + 25, 12, Math.PI, 0, false);
                    ctx.fill();
                } else if (m.type === 'bat') {
                    ctx.fillStyle = '#9b59b6';
                    ctx.fillRect(mx + 10, my + 15, 20, 10);
                } else if (m.type === 'goblin') {
                    ctx.fillStyle = '#27ae60';
                    ctx.fillRect(mx + 12, my + 10, 16, 20);
                } else if (m.type === 'spider') {
                    ctx.fillStyle = '#34495e';
                    ctx.fillRect(mx + 10, my + 12, 20, 14);
                } else { // Golem / Demon (Tầng cao)
                    ctx.fillStyle = '#e67e22';
                    ctx.fillRect(mx + 8, my + 6, 24, 28);
                }

                // Thanh HP nhỏ trên đầu quái
                ctx.fillStyle = '#000';
                ctx.fillRect(mx + 5, my + 2, 30, 4);
                ctx.fillStyle = '#e74c3c';
                ctx.fillRect(mx + 5, my + 2, (m.hp / m.maxHp) * 30, 4);
            });

            // 3. Vẽ Nhân vật Hiệp sĩ
            let px = player.x * TILE_SIZE;
            let py = player.y * TILE_SIZE;
            
            ctx.fillStyle = '#2980b9'; // Áo choàng
            ctx.fillRect(px + 8, py + 12, 24, 20);
            ctx.fillStyle = '#bdc3c7'; // Giáp
            ctx.fillRect(px + 12, py + 8, 16, 16);
            ctx.fillStyle = '#8e44ad'; // Mũ
            ctx.fillRect(px + 12, py + 4, 16, 8);
            ctx.fillStyle = '#ecf0f1'; // Kiếm
            ctx.fillRect(px + 28, py + 14, 8, 4);

            // 4. Vẽ Khung HUD Giao diện thông tin
            ctx.fillStyle = 'rgba(15, 15, 20, 0.9)';
            ctx.fillRect(10, 10, 220, 85);
            ctx.strokeStyle = '#555';
            ctx.strokeRect(10, 10, 220, 85);

            // Thanh HP người chơi
            ctx.fillStyle = '#c0392b';
            ctx.fillRect(20, 20, 150, 16);
            ctx.fillStyle = '#2ecc71';
            let hpW = Math.max(0, (player.hp / player.maxHp) * 150);
            ctx.fillRect(20, 20, hpW, 16);
            
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 11px "Courier New"';
            ctx.fillText(`HP: ${Math.max(0, player.hp)}/${player.maxHp}`, 26, 32);

            // Các chỉ số LVL, SCORE, FLOOR, KEYS
            ctx.fillStyle = '#f1c40f';
            ctx.fillText(`LVL: ${player.lvl}`, 20, 52);
            ctx.fillText(`SCORE: ${player.score}`, 20, 72);
            
            ctx.fillStyle = '#3498db';
            ctx.fillText(`FLOOR: ${player.floor}F`, 130, 52);
            ctx.fillStyle = '#e67e22';
            ctx.fillText(`KEYS: ${player.keys}`, 130, 72);
        }

        drawGame();
    </script>
</body>
</html>
"""

components.html(game_html, height=450)
