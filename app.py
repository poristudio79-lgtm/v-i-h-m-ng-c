import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Pixel Dungeon: Detailed Legs & Sword Anatomy",
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

st.markdown("<h1 class='main-title'>⚔️ PIXEL DUNGEON: DETAILED HERO & SWORD 🗡️</h1>", unsafe_allow_html=True)
st.markdown("<div class='instructions'>Dùng phím <b>W, A, S, D</b> để di chuyển. Nhân vật có chân chuyển động, thanh kiếm có đầy đủ đế, thân và mũi kiếm sắc bén!</div>", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Detailed Sword Pixel Dungeon</title>
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
            pommelColor: "#512e5f",  // Đế chuôi kiếm
            hiltColor: "#784212",    // Chuôi cầm / Cán kiếm
            guardColor: "#d35400",   // Chắn kiếm (Bảo vệ tay)
            bladeColor: "#e59866",   // Thân lưỡi kiếm
            tipColor: "#f5b041",     // Mũi kiếm
            damage: 25
        };

        let currentMap = [];
        let monsters = [];
        let exitCoord = { x: 13, y: 8 };
        let monsterMoveTimer = null;
        
        let idleCounter = 0;
        let slashEffect = null;

        // --- HỆ THỐNG ÂM THANH KỊCH TÍNH (EPIC BGM) ---
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

            bgmInterval = setInterval(() => {
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
        // ----------------------------------------------

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

        // --- QUÁI TỰ ĐỘNG DI CHUYỂN LIÊN TỤC ---
        function startMonsterAI() {
            if (monsterMoveTimer) clearInterval(monsterMoveTimer);

            monsterMoveTimer = setInterval(() => {
                monsters.forEach(m => {
                    let possibleMoves = [];
                    let directions = [
                        { x: 0, y: -1 }, { x: 0, y: 1 },
                        { x: -1, y: 0 }, { x: 1, y: 0 }
                    ];

                    directions.forEach(d => {
                        let nextX = m.x + d.x;
                        let nextY = m.y + d.y;
                        if (nextY >= 0 && nextY < ROWS && nextX >= 0 && nextX < COLS) {
                            if (currentMap[nextY][nextX] !== 1) {
                                possibleMoves.push({ x: nextX, y: nextY });
                            }
                        }
                    });

                    if (possibleMoves.length > 0) {
                        possibleMoves.sort((a, b) => {
                            let distA = Math.abs(a.x - player.x) + Math.abs(a.y - player.y);
                            let distB = Math.abs(b.x - player.x) + Math.abs(b.y - player.y);
                            return distA - distB;
                        });
                        m.x = possibleMoves[0].x;
                        m.y = possibleMoves[0].y;
                    }
                });
