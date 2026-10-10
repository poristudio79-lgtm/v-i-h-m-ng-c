import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Pixel Dungeon RPG: Ultimate Edition",
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

st.markdown("<h1 class='main-title'>⚔️ PIXEL DUNGEON: ULTIMATE HERO RPG 🗡️</h1>", unsafe_allow_html=True)
st.markdown("<div class='instructions'>Dùng phím <b>W, A, S, D</b> để di chuyển. Tiêu diệt quái vật để lên cấp (Level Up) thay đổi trang phục, mở rương nâng cấp vũ khí!</div>", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Ultimate Pixel Dungeon RPG</title>
    <style>
        body {
            background-color: #050508;
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
            border: 5px solid #4a1515;
            background-color: #0d0b10;
            box-shadow: 0 0 40px rgba(220, 20, 60, 0.5);
            position: relative;
        }
        canvas {
            display: block;
            image-rendering: pixelated;
        }
        #audio-btn {
            margin-top: 12px;
            background-color: #b03a2e;
            color: #fff;
            border: none;
            padding: 10px 20px;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            cursor: pointer;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: 0.2s;
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
    <button id="audio-btn" onclick="toggleAudio()">🔥 Bật / Tắt Nhạc Hầm Ngục Epic</button>

    <script>
        /* ==========================================================
           1. KHỞI TẠO HỆ THỐNG & GAME ENGINE CORE (~500 DÒNG CODE)
           ========================================================== */
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const TILE_SIZE = 40;
        const COLS = 15;
        const ROWS = 10;

        // Đối tượng người chơi (Player)
        let player = {
            x: 1,
            y: 1,
            hp: 120,
            maxHp: 120,
            score: 0,
            floor: 1,
            lvl: 1,
            keys: 0,
            // Trang phục mặc định (Level 1)
            armorName: "Giáp Tập Sự",
            cloakColor: "#1b4f72",
            armorColor: "#bdc3c7",
            helmetColor: "#566573",
            featherColor: "#e74c3c",
            // Vũ khí mặc định
            weaponName: "Kiếm Gỗ Cũ",
            pommelColor: "#512e5f",
            hiltColor: "#784212",
            guardColor: "#d35400",
            bladeColor: "#e59866",
            tipColor: "#f5b041",
            damage: 30
        };

        let currentMap = [];
        let monsters = [];
        let exitCoord = { x: 13, y: 8 };
        let monsterMoveTimer = null;
        
        let idleCounter = 0;
        let slashEffect = null;
        let floatingTexts = []; // Mảng chứa hiệu ứng chữ sát thương bay lên

        // --- HỆ THỐNG ÂM THANH CHIPTUNE 8-BIT (WEB AUDIO API) ---
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
                document.getElementById("audio-btn").innerText = "🔇 Tắt Nhạc Hầm Ngục Epic";
            } else {
                stopBGM();
                isPlayingBGM = false;
                document.getElementById("audio-btn").innerText = "🔥 Bật / Tắt Nhạc Hầm Ngục Epic";
            }
        }

        function startEpicBGM() {
            const epicNotes = [220, 246.94, 261.63, 293.66, 329.63, 293.66, 261.63, 196, 220, 329.63, 392, 349.23];
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
            }, 170);
        }

        function stopBGM() {
            if (bgmInterval) {
                clearInterval(bgmInterval);
                bgmInterval = null;
            }
        }

        /* ==========================================================
           2. HỆ THỐNG TIẾN HÓA TRANG PHỤC & VŨ KHÍ THEO LEVEL
           ========================================================== */
        function updateHeroGear() {
            if (player.lvl >= 3) {
                // Cấp 3: Chiến thần hầm ngục tối thượng
                player.armorName = "Giáp Chiến Thần";
                player.cloakColor = "#78281f"; // Áo choàng đỏ huyết long
                player.armorColor = "#f1c40f"; // Giáp vàng hoàng kim
                player.helmetColor = "#7b241c";
                player.featherColor = "#ffffff";
                
                player.weaponName = "Thương Thần Thánh";
                player.pommelColor = "#512e5f";
                player.hiltColor = "#f39c12";
                player.guardColor = "#c0392b";
                player.bladeColor = "#f1c40f";
                player.tipColor = "#ffffff";
                player.damage = 75;
            } else if (player.lvl === 2) {
                // Cấp 2: Hiệp sĩ hoàng gia
                player.armorName = "Giáp Hoàng Gia";
                player.cloakColor = "#117864"; // Áo choàng ngọc bích
                player.armorColor = "#85c1e9"; // Giáp bạc xanh
                player.helmetColor = "#2e4053";
                player.featherColor = "#f39c12";
                
                player.weaponName = "Kiếm Sắt Sắc";
                player.pommelColor = "#2c3e50";
                player.hiltColor = "#7f8c8d";
                player.guardColor = "#bdc3c7";
                player.bladeColor = "#ecf0f1";
                player.tipColor = "#ffffff";
                player.damage = 45;
            } else {
                // Cấp 1: Hiệp sĩ tập sự
                player.armorName = "Giáp Tập Sự";
                player.cloakColor = "#1b4f72";
                player.armorColor = "#bdc3c7";
                player.helmetColor = "#566573";
                player.featherColor = "#e74c3c";
                
                player.weaponName = "Kiếm Gỗ Cũ";
                player.pommelColor = "#512e5f";
                player.hiltColor = "#784212";
                player.guardColor = "#d35400";
                player.bladeColor = "#e59866";
                player.tipColor = "#f5b041";
                player.damage = 30;
            }
        }

        /* ==========================================================
           3. HỆ THỐNG MAP & TẠO QUÁI VẬT THEO TẦNG (FLOOR)
           ========================================================== */
        function loadFloor(floorNum) {
            player.x = 1;
            player.y = 1;
            updateHeroGear();

            if (floorNum === 1) {
                // Bản đồ Tầng 1: Hành lang hầm mộ đá
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
                    { x: 12, y: 5, hp: 40, maxHp: 40, type: 'slime' },
                    { x: 6, y: 3, hp: 35, maxHp: 35, type: 'bat' },
                    { x: 3, y: 7, hp: 45, maxHp: 45, type: 'slime' }
                ];
            } else if (floorNum === 2) {
                // Bản đồ Tầng 2: Mê cung ziczac hẹp
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
                    { x: 7, y: 3, hp: 75, maxHp: 75, type: 'goblin' },
                    { x: 3, y: 5, hp: 65, maxHp: 65, type: 'spider' },
                    { x: 11, y: 7, hp: 80, maxHp: 80, type: 'goblin' }
                ];
            } else {
                // Bản đồ Tầng 3+: Cung điện quỷ vương
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
                    { x: 7, y: 4, hp: 130, maxHp: 130, type: 'golem' },
                    { x: 3, y: 1, hp: 110, maxHp: 110, type: 'demon' },
                    { x: 13, y: 7, hp: 120, maxHp: 120, type: 'demon' }
                ];
            }
            currentMap[exitCoord.y][exitCoord.x] = 2; // Cửa xuống tầng
        }

        loadFloor(1);

        /* ==========================================================
           4. HỆ THỐNG AI & LOGIC DI CHUYỂN THỜI GIAN THỰC CỦA QUÁI
           ========================================================== */
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

                // Kiểm tra quái tấn công người chơi
                monsters.forEach(function(m) {
                    if (Math.abs(m.x - player.x) + Math.abs(m.y - player.y) === 1) {
                        let monsterDmg = 10 + (player.floor * 4);
                        player.hp -= monsterDmg;
                        floatingTexts.push({ text: "-" + monsterDmg, x: player.x * TILE_SIZE + 10, y: player.y * TILE_SIZE, color: '#e74c3c', timer: 25 });
                        
                        if (player.hp <= 0) {
                            alert("💀 GAME OVER! Bạn đã hy sinh ở Tầng " + player.floor + ". Điểm số cuối cùng: " + player.score);
                            player.hp = 120;
                            player.maxHp = 120;
                            player.score = 0;
                            player.floor = 1;
                            player.lvl = 1;
                            player.keys = 0;
                            loadFloor(1);
                        }
                    }
                });

                drawGame();
            }, 1200);
        }

        startMonsterAI();

        /* ==========================================================
           5. XỬ LÝ SỰ KIỆN BÀN PHÍM & TƯƠNG TÁC GAME
           ========================================================== */
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
                        // Tấn công quái vật
                        monsters[mIndex].hp -= player.damage;
                        player.score += 150;
                        slashEffect = { x: newX, y: newY, timer: 6 };
                        floatingTexts.push({ text: "-" + player.damage, x: newX * TILE_SIZE + 10, y: newY * TILE_SIZE, color: '#f1c40f', timer: 25 });

                        if (monsters[mIndex].hp <= 0) {
                            monsters.splice(mIndex, 1);
                            player.score += 350;
                            
                            // Check thăng cấp Level
                            if (player.score >= player.lvl * 900 && player.lvl < 3) {
                                player.lvl++;
                                player.maxHp += 40;
                                player.hp = player.maxHp;
                                updateHeroGear();
                                alert("🎉 THĂNG CẤP! Bạn đã đạt Cấp độ " + player.lvl + "! Trang phục tiến hóa thành: " + player.armorName);
                            }
                        }
                    } else if (tile === 3) {
                        // Nhặt rương báu
                        player.score += 500;
                        player.keys += 1;
                        player.hp = Math.min(player.maxHp, player.hp + 45);
                        currentMap[newY][newX] = 0;
                        floatingTexts.push({ text: "+45 HP", x: newX * TILE_SIZE, y: newY * TILE_SIZE, color: '#2ecc71', timer: 30 });
                    } else if (tile === 2) {
                        // Xuống tầng mới
                        player.floor++;
                        player.score += 1200;
                        alert("⚡ Chúc mừng! Đã bước xuống Tầng " + player.floor + ". Bản đồ và thử thách mới xuất hiện!");
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

        //
