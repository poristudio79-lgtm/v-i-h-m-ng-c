import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Pixel Dungeon: Armed Hero",
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

st.markdown("<h1 class='main-title'>⚔️ PIXEL DUNGEON CRAWLER 🗡️</h1>", unsafe_allow_html=True)
st.markdown("<div class='instructions'>Dùng phím <b>W, A, S, D</b> để di chuyển. Nhân vật có hai tay cầm kiếm nghiêng sang phải cực kỳ rõ nét!</div>", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Pixel Dungeon Armed Hero</title>
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
            border: 4px solid #5a1818;
            background-color: #121016;
            box-shadow: 0 0 35px rgba(200, 0, 0, 0.4);
            position: relative;
        }
        canvas {
            display: block;
            image-rendering: pixelated;
        }
        #audio-btn {
            margin-top: 10px;
            background-color: #c0392b;
            color: #fff;
            border: none;
            padding: 8px 16px;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            cursor: pointer;
            border-radius: 4px;
        }
        #audio-btn:hover {
            background-color: #e74c3c;
        }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="gameCanvas" width="600" height="400"></canvas>
    </div>
    <button id="audio-btn" onclick="toggleAudio()">🔥 Bật / Tắt Nhạc Chiến Đấu Kịch Tính</button>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const TILE_SIZE = 40;
        const COLS = 15;
        const ROWS = 10;

        let player = {
            x: 1,
            y: 1,
            hp: 100,
            maxHp: 100,
            score: 0,
            floor: 1,
            keys: 0,
            weaponName: "Kiếm Gỗ Cũ",
            pommelColor: "#512e5f",
            hiltColor: "#784212",
            guardColor: "#d35400",
            bladeColor: "#e59866",
            tipColor: "#f5b041",
            damage: 25
        };

        let currentMap = [];
        let monsters = [];
        let exitCoord = { x: 13, y: 8 };
        let monsterMoveTimer = null;
        
        let idleCounter = 0;
        let slashEffect = null;

        // --- ÂM THANH KỊCH TÍNH (WEB AUDIO API) ---
        let audioCtx = null;
        let isPlayingBGM = false;
        let bgmInterval = null;

        function toggleAudio() {
            if (!isPlayingBGM) {
                if (!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                }
                if (audioCtx.state === 'suspended') {
                    audioCtx.resume();
                }
                startEpicBGM();
                isPlayingBGM = true;
                document.getElementById("audio-btn").innerText = "🔇 Tắt Nhạc Kịch Tính";
            } else {
                stopBGM();
                isPlayingBGM = false;
                document.getElementById("audio-btn").innerText = "🔥 Bật / Tắt Nhạc Chiến Đấu Kịch Tính";
            }
        }

        function startEpicBGM() {
            const epicNotes = [220, 220, 261.63, 293.66, 329.63, 293.66, 261.63, 196, 220, 329.63, 392, 329.63];
            let noteIndex = 0;

            bgmInterval = setInterval(function() {
                if (!isPlayingBGM || !audioCtx) return;
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();

                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(epicNotes[noteIndex], audioCtx.currentTime);

                gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);

                osc.connect(gain);
                gain.connect(audioCtx.destination);

                osc.start();
                osc.stop(audioCtx.currentTime + 0.18);

                noteIndex = (noteIndex + 1) % epicNotes.length;
            }, 180);
        }

        function stopBGM() {
            if (bgmInterval) {
                clearInterval(bgmInterval);
                bgmInterval = null;
            }
        }

        function updateWeapon() {
            if (player.keys >= 2) {
                player.weaponName = "Thương Thần Thánh";
                player.pommelColor = "#7d3c98";
                player.hiltColor = "#f39c12";
                player.guardColor = "#e74c3c";
                player.bladeColor = "#f1c40f";
                player.tipColor = "#ffffff";
                player.damage = 65;
            } else if (player.keys === 1) {
                player.weaponName = "Kiếm Sắt Sắc";
                player.pommelColor = "#2c3e50";
                player.hiltColor = "#7f8c8d";
                player.guardColor = "#bdc3c7";
                player.bladeColor = "#ecf0f1";
                player.tipColor = "#ffffff";
                player.damage = 40;
            } else {
                player.weaponName = "Kiếm Gỗ Cũ";
                player.pommelColor = "#512e5f";
                player.hiltColor = "#784212";
                player.guardColor = "#d35400";
                player.bladeColor = "#e59866";
                player.tipColor = "#f5b041";
                player.damage = 25;
            }
        }

        function loadFloor(floorNum) {
            player.x = 1;
            player.y = 1;
            updateWeapon();

            if (floorNum === 1) {
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
                    { x: 12, y: 5, hp: 30, maxHp: 30, type: 'slime' },
                    { x: 6, y: 3, hp: 25, maxHp: 25, type: 'bat' },
                    { x: 3, y: 7, hp: 35, maxHp: 35, type: 'slime' }
                ];
            } else if (floorNum === 2) {
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
                    { x: 7, y: 3, hp: 60, maxHp: 60, type: 'goblin' },
                    { x: 3, y: 5, hp: 50, maxHp: 50, type: 'spider' },
                    { x: 11, y: 7, hp: 70, maxHp: 70, type: 'goblin' }
                ];
            } else {
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
                    { x: 7, y: 4, hp: 110, maxHp: 110, type: 'golem' },
                    { x: 3, y: 1, hp: 90, maxHp: 90, type: 'demon' },
                    { x: 13, y: 7, hp: 100, maxHp: 100, type: 'demon' }
                ];
            }
            currentMap[exitCoord.y][exitCoord.x] = 2;
        }

        loadFloor(1);

        function startMonsterAI() {
            if (monsterMoveTimer) clearInterval(monsterMoveTimer);

            monsterMoveTimer = setInterval(function() {
                monsters.forEach(function(m) {
                    let possibleMoves = [];
                    let directions = [
                        { x: 0, y: -1 }, { x: 0, y: 1 },
                        { x: -1, y: 0 }, { x: 1, y: 0 }
                    ];

                    directions.forEach(function(d) {
                        let nextX = m.x + d.x;
                        let nextY = m.y + d.y;
                        if (nextY >= 0 && nextY < ROWS && nextX >= 0 && nextX < COLS) {
                            if (currentMap[nextY][nextX] !== 1) {
                                possibleMoves.push({ x: nextX, y: nextY });
                            }
                        }
                    });

                    if (possibleMoves.length > 0) {
                        possibleMoves.sort(function(a, b) {
                            let distA = Math.abs(a.x - player.x) + Math.abs(a.y - player.y);
                            let distB = Math.abs(b.x - player.x) + Math.abs(b.y - player.y);
                            return distA - distB;
                        });
                        m.x = possibleMoves[0].x;
                        m.y = possibleMoves[0].y;
                    }
                });

                monsters.forEach(function(m) {
                    if (Math.abs(m.x - player.x) + Math.abs(m.y - player.y) === 1) {
                        let monsterDmg = 8 + (player.floor * 3);
                        player.hp -= monsterDmg;
                        if (player.hp <= 0) {
                            alert("💀 Game Over! Bạn đã ngã xuống ở Tầng " + player.floor + ". Điểm: " + player.score);
                            player.hp = 100;
                            player.score = 0;
                            player.floor = 1;
                            player.keys = 0;
                            loadFloor(1);
                        }
                    }
                });

                drawGame();
            }, 1200);
        }

        startMonsterAI();

        window.addEventListener('keydown', function(e) {
            if(["Space","ArrowUp","ArrowDown","ArrowLeft","ArrowRight","w","a","s","d"].indexOf(e.key) > -1) {
                e.preventDefault();
            }

            let newX = player.x;
            let newY = player.y;

            if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') newY--;
            if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') newY++;
            if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') newX--;
            if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') newX++;

            if (newY >= 0 && newY < ROWS && newX >= 0 && newX < COLS) {
                let tile = currentMap[newY][newX];

                if (tile !== 1) {
                    let mIndex = monsters.findIndex(m => m.x === newX && m.y === newY);
                    if (mIndex !== -1) {
                        monsters[mIndex].hp -= player.damage;
                        player.score += 100;
                        slashEffect = { x: newX, y: newY, timer: 6 };

                        if (monsters[mIndex].hp <= 0) {
                            monsters.splice(mIndex, 1);
                            player.score += 250;
                        }
                    } else if (tile === 3) {
                        player.score += 400;
                        player.keys += 1;
                        player.hp = Math.min(player.maxHp, player.hp + 35);
                        currentMap[newY][newX] = 0;
                        updateWeapon();
                    } else if (tile === 2) {
                        player.floor++;
                        player.score += 1000;
                        alert("⚡ Đã bước xuống Tầng " + player.floor + "! Bản đồ hoàn toàn mới.");
                        loadFloor(player.floor);
                        startMonsterAI();
                        drawGame();
                        return;
                    } else {
                        player.x = newX;
                        player.y = newY;
                    }
                }
            }

            drawGame();
        });

        function gameLoop() {
            idleCounter += 0.08;
            drawGame();
            requestAnimationFrame(gameLoop);
        }

        function drawGame() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ Map
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    let x = c * TILE_SIZE;
                    let y = r * TILE_SIZE;

                    if (currentMap[r][c] === 1) {
                        ctx.fillStyle = player.floor === 2 ? '#1f4e5b' : (player.floor >= 3 ? '#5b1f1f' : '#2c223b');
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.fillStyle = player.floor === 2 ? '#2874a6' : (player.floor >= 3 ? '#922b21' : '#3e3154');
                        ctx.fillRect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4);
                    } else {
                        ctx.fillStyle = '#1b1726';
                        ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                        ctx.strokeStyle = '#252033';
                        ctx.strokeRect(x, y, TILE_SIZE, TILE_SIZE);
                    }

                    if (currentMap[r][c] === 2) {
                        ctx.fillStyle = '#f1c40f';
                        ctx.fillRect(x + 4, y + 4, TILE_SIZE - 8, TILE_SIZE - 8);
                    }

                    if (currentMap[r][c] === 3) {
                        ctx.fillStyle = '#d35400';
                        ctx.fillRect(x + 8, y + 12, 24, 18);
                        ctx.fillStyle = '#f39c12';
                        ctx.fillRect(x + 16, y + 18, 8, 6);
                    }
                }
            }

            // 2. Vẽ quái vật
            monsters.forEach(function(m) {
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
                } else {
                    ctx.fillStyle = '#e67e22';
                    ctx.fillRect(mx + 8, my + 6, 24, 28);
                }

                ctx.fillStyle = '#000';
                ctx.fillRect(mx + 5, my + 2, 30, 4);
                ctx.fillStyle = '#e74c3c';
                ctx.fillRect(mx + 5, my + 2, Math.max(0, (m.hp / m.maxHp) * 30), 4);
            });

            // 3. Hiệu ứng vết chém
            if (slashEffect && slashEffect.timer > 0) {
                let sx = slashEffect.x * TILE_SIZE;
                let sy = slashEffect.y * TILE_SIZE;
                
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 4;
                ctx.beginPath();
                ctx.moveTo(sx + 8, sy + 8);
                ctx.lineTo(sx + 32, sy + 32);
                ctx.stroke();

                ctx.strokeStyle = '#f1c40f';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(sx + 32, sy + 8);
                ctx.lineTo(sx + 8, sy + 32);
                ctx.stroke();

                slashEffect.timer--;
            }

            // 4. VẼ NHÂN VẬT CHÍNH CÓ TAY CẦM KIẾM NGHIÊNG SANG PHẢI RÕ RÀNG
            let px = player.x * TILE_SIZE;
            let bounce = Math.sin(idleCounter) * 2; 
            let py = (player.y * TILE_SIZE) + bounce;

            // Chân nhún nhảy
            ctx.fillStyle = '#117864';
            let legOffset = Math.sin(idleCounter * 2) > 0 ? 1 : -1;
            ctx.fillRect(px + 10, py + 30, 4, 6 + legOffset);
            ctx.fillRect(px + 18, py + 30, 4, 6 - legOffset);

            // Áo choàng xanh thẫm
            ctx.fillStyle = '#1b4f72';
            ctx.fillRect(px + 6, py + 12, 16, 20);

            // Giáp ngực (thân người)
            ctx.fillStyle = '#bdc3c7';
            ctx.fillRect(px + 10, py + 14, 14, 14);
            ctx.fillStyle = '#7f8c8d';
            ctx.fillRect(px + 10, py + 14, 14, 3);

            // Mũ giáp
            ctx.fillStyle = '#566573';
            ctx.fillRect(px + 10, py + 6, 14, 10);
            ctx.fillStyle = '#000000';
            ctx.fillRect(px + 12, py + 9, 8, 3);
            ctx.fillStyle = '#e74c3c';
            ctx.fillRect(px + 14, py + 3, 4, 4);

            // --- HAI CÁNH TAY CẦM CÁN KIẾM LỆCH SANG PHẢI RÕ RÀNG ---
            ctx.fillStyle = '#bdc3c7';
            ctx.fillRect(px + 20, py + 16, 8, 4);
            ctx.fillStyle = '#e0e0e0';
            ctx.fillRect(px + 26, py + 16, 3, 4);

            ctx.fillStyle = '#bdc3c7';
            ctx.fillRect(px + 22, py + 21, 6, 4);
            ctx.fillStyle = '#e0e0e0';
            ctx.fillRect(px + 26, py + 21, 3, 4);

            // --- CẤU TRÚC THANH KIẾM VỚI ĐẦY ĐỦ BỘ PHẬN ---
            ctx.fillStyle = player.pommelColor;
            ctx.fillRect(px + 28, py + 27, 4, 3);
            ctx.fillStyle = player.hiltColor;
            ctx.fillRect(px + 28, py + 20, 4, 7);
            ctx.fillStyle = player.guardColor;
            ctx.fillRect(px + 25, py + 17, 10, 3);
            ctx.fillStyle = player.bladeColor;
            ctx.fillRect(px + 28, py + 7, 4, 10);
            ctx.fillStyle = player.tipColor;
            ctx.beginPath();
            ctx.moveTo(px + 28, py + 7);
            ctx.lineTo(px + 30, py + 2);
            ctx.lineTo(px + 32, py + 7);
            ctx.fill();

            // 5. Khung giao diện HUD
            ctx.fillStyle = 'rgba(15, 15, 20, 0.92)';
            ctx.fillRect(10, 10, 240, 100);
            ctx.strokeStyle = '#555';
            ctx.strokeRect(10, 10, 240, 100);

            ctx.fillStyle = '#c0392b';
            ctx.fillRect(20, 18, 160, 16);
            ctx.fillStyle = '#2ecc71';
            let hpW = Math.max(0, (player.hp / player.maxHp) * 160);
            ctx.fillRect(20, 18, hpW, 16);
            
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 11px "Courier New"';
            ctx.fillText('HP: ' + Math.max(0, player.hp) + '/' + player.maxHp, 26, 30);

            ctx.fillStyle = '#f1c40f';
            ctx.fillText('SCORE: ' + player.score, 20, 48);
            
            ctx.fillStyle = '#3498db';
            ctx.fillText('FLOOR: ' + player.floor + 'F', 140, 48);
            
            ctx.fillStyle = '#e67e22';
            ctx.fillText('KEYS: ' + player.keys, 20, 68);

            ctx.fillStyle = player.bladeColor;
            ctx.fillText('WEAPON: ' + player.weaponName, 20, 90);
        }

        gameLoop();
    </script>
</body>
</html>
"""

components.html(game_html, height=490)
