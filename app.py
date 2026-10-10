import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Pixel Dungeon Crawler",
    page_icon="🗡️",
    layout="centered"
)

st.title("🗡️ Pixel Dungeon Crawler")
st.markdown("Sử dụng các phím **W, A, S, D** hoặc **Phím mũi tên** để di chuyển. Tiêu diệt quái vật (màu đỏ) và tìm lối thoát (ô vàng)!")

# Mã HTML/JS của tựa game Pixel Dungeon
game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Pixel Dungeon</title>
    <style>
        body {
            background-color: #1a1a1a;
            color: white;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        canvas {
            border: 4px solid #444;
            background-color: #111;
            image-rendering: pixelated;
            box-shadow: 0 0 20px rgba(0,0,0,0.8);
        }
        #ui {
            margin-bottom: 10px;
            font-size: 18px;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div id="ui">Máu: <span id="hp">100</span> | Điểm: <span id="score">0</span> | Tầng: <span id="floor">1</span></div>
    <canvas id="gameCanvas" width="400" height="400"></canvas>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const TILE_SIZE = 40;
        const GRID_SIZE = 10; // 10x10 tiles = 400x400 pixels

        let player = { x: 1, y: 1, hp: 100, maxHp: 100, score: 0, floor: 1 };
        let monsters = [];
        let exit = { x: 8, y: 8 };

        // 0: Đường đi, 1: Tường
        let map = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,0,1],
            [1,0,1,0,1,0,1,1,0,1],
            [1,0,1,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,0,1,0,1],
            [1,0,0,0,0,1,0,0,0,1],
            [1,1,1,0,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1]
        ];

        function spawnMonsters() {
            monsters = [
                { x: 5, y: 1, hp: 20, color: '#e74c3c' },
                { x: 8, y: 5, hp: 30, color: '#c0392b' },
                { x: 2, y: 7, hp: 20, color: '#e74c3c' }
            ];
        }

        spawnMonsters();

        // Xử lý bàn phím
        window.addEventListener('keydown', e => {
            let newX = player.x;
            let newY = player.y;

            if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') newY--;
            if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') newY++;
            if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') newX--;
            if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') newX++;

            // Kiểm tra va chạm tường
            if (map[newY] && map[newY][newX] === 0) {
                // Kiểm tra va chạm quái vật
                let hitMonsterIndex = monsters.findIndex(m => m.x === newX && m.y === newY);
                if (hitMonsterIndex !== -1) {
                    // Đánh quái
                    monsters[hitMonsterIndex].hp -= 20;
                    player.score += 10;
                    if (monsters[hitMonsterIndex].hp <= 0) {
                        monsters.splice(hitMonsterIndex, 1);
                    }
                } else {
                    player.x = newX;
                    player.y = newY;
                }

                // Kiểm tra lối thoát
                if (player.x === exit.x && player.y === exit.y) {
                    player.floor++;
                    player.score += 100;
                    player.x = 1;
                    player.y = 1;
                    spawnMonsters();
                    alert("Chúc mừng bạn đã qua tầng " + (player.floor - 1) + "!");
                }

                // Quái di chuyển tấn công người chơi
                monsters.forEach(m => {
                    if (Math.abs(m.x - player.x) + Math.abs(m.y - player.y) === 1) {
                        player.hp -= 10;
                        if (player.hp <= 0) {
                            alert("Game Over! Điểm của bạn: " + player.score);
                            player.hp = player.maxHp;
                            player.score = 0;
                            player.floor = 1;
                            player.x = 1;
                            player.y = 1;
                            spawnMonsters();
                        }
                    }
                });
            }

            updateUI();
            draw();
        });

        function updateUI() {
            document.getElementById('hp').innerText = player.hp;
            document.getElementById('score').innerText = player.score;
            document.getElementById('floor').innerText = player.floor;
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ Map
            for (let r = 0; r < GRID_SIZE; r++) {
                for (let c = 0; c < GRID_SIZE; c++) {
                    if (map[r][c] === 1) {
                        ctx.fillStyle = '#2c3e50'; // Tường
                        ctx.fillRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                    } else {
                        ctx.fillStyle = '#34495e'; // Sàn
                        ctx.fillRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                        ctx.strokeStyle = '#2c3e50';
                        ctx.strokeRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                    }
                }
            }

            // Vẽ Lối thoát
            ctx.fillStyle = '#f1c40f';
            ctx.fillRect(exit.x * TILE_SIZE + 5, exit.y * TILE_SIZE + 5, TILE_SIZE - 10, TILE_SIZE - 10);

            // Vẽ Quái vật
            monsters.forEach(m => {
                ctx.fillStyle = m.color;
                ctx.fillRect(m.x * TILE_SIZE + 8, m.y * TILE_SIZE + 8, TILE_SIZE - 16, TILE_SIZE - 16);
            });

            // Vẽ Người chơi (Hiệp sĩ)
            ctx.fillStyle = '#3498db';
            ctx.fillRect(player.x * TILE_SIZE + 8, player.y * TILE_SIZE + 8, TILE_SIZE - 16, TILE_SIZE - 16);
        }

        draw();
    </script>
</body>
</html>
"""

# Hiển thị game trong Streamlit
components.html(game_html, height=500)
