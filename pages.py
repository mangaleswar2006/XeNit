def get_new_tab_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>XeNit</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');

            :root {
                --bg: #09090b;
                --card-bg: rgba(24, 24, 27, 0.4);
                --accent: #00F0FF;
                --accent-glow: rgba(0, 240, 255, 0.4);
                --text: #FAFAFA;
            }
            body {
                background-color: var(--bg);
                color: var(--text);
                font-family: 'Inter', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                overflow: hidden;
            }

            /* Animated Background: Digital Horizon */
            .grid-bg {
                position: absolute;
                width: 200%;
                height: 200%;
                background-image: 
                    linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
                background-size: 50px 50px;
                transform: perspective(500px) rotateX(60deg) translateY(-100px) translateZ(-200px);
                animation: grid-move 20s linear infinite;
                z-index: -2;
            }
            @keyframes grid-move {
                0% { transform: perspective(500px) rotateX(60deg) translateY(0) translateZ(-200px); }
                100% { transform: perspective(500px) rotateX(60deg) translateY(50px) translateZ(-200px); }
            }

            /* Central Glow */
            .glow-spot {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 60vw;
                height: 60vw;
                transform: translate(-50%, -50%);
                background: radial-gradient(circle, rgba(0, 240, 255, 0.05) 0%, rgba(0,0,0,0) 70%);
                z-index: -1;
                pointer-events: none;
            }

            .container {
                z-index: 10;
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
                max-width: 800px;
            }

            .logo-container {
                text-align: center;
                margin-bottom: 40px;
            }

            .logo {
                font-family: 'Orbitron', sans-serif;
                font-size: 7rem;
                font-weight: 900;
                letter-spacing: -2px;
                color: #FFF;
                text-transform: uppercase;
                text-shadow: 0 0 20px var(--accent-glow), 0 0 60px rgba(0, 240, 255, 0.2);
                -webkit-text-stroke: 3px #FFF; /* Artificial bolding */
                margin: 0;
                line-height: 1;
            }
            
            .sub-logo {
                font-family: 'Orbitron', sans-serif;
                font-size: 1.2rem;
                font-weight: 700; /* Bold */
                letter-spacing: 8px;
                color: var(--accent);
                opacity: 0.8;
                margin-top: 10px;
                text-shadow: 0 0 10px var(--accent-glow);
            }

            .search-wrapper {
                position: relative;
                width: 100%;
                max-width: 650px;
            }

            .search-icon {
                position: absolute;
                left: 25px;
                top: 50%;
                transform: translateY(-50%);
                width: 24px;
                height: 24px;
                fill: #A1A1AA;
                transition: fill 0.3s;
                z-index: 2;
            }

            .search-input {
                width: 100%;
                padding: 20px 20px 20px 60px; /* Space for icon */
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(0, 0, 0, 0.4);
                color: #FFF;
                font-size: 1.2rem;
                backdrop-filter: blur(20px);
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                outline: none;
                box-sizing: border-box;
            }

            .search-input:focus {
                border-color: var(--accent);
                box-shadow: 0 0 0 1px var(--accent), 0 0 40px rgba(0, 240, 255, 0.15);
                background: rgba(0, 0, 0, 0.8);
            }

            .search-input:focus + .search-icon {
                fill: var(--accent);
            }

            .shortcuts {
                margin-top: 60px;
                display: flex;
                gap: 20px;
            }
            .shortcut {
                width: 80px;
                height: 80px;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: #888;
                text-decoration: none;
                transition: all 0.3s;
                backdrop-filter: blur(5px);
            }
            .shortcut:hover {
                background: rgba(0, 240, 255, 0.05);
                border-color: var(--accent);
                color: #FFF;
                transform: translateY(-5px);
                box-shadow: 0 5px 20px rgba(0, 240, 255, 0.1);
            }
            .shortcut-icon { font-size: 1.5rem; margin-bottom: 5px; }
            .shortcut span { font-size: 0.75rem; font-weight: 500; }
        </style>
    </head>
    <body>
        <div class="grid-bg"></div>
        <div class="glow-spot"></div>

        <div class="container">
            <div class="logo-container">
                <div class="logo">XeNit</div>
                <div class="sub-logo">ULTRA</div>
            </div>

            <div class="search-wrapper">
                <input type="text" class="search-input" placeholder="Search the future..." id="searchInput">
                <svg class="search-icon" viewBox="0 0 24 24">
                    <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
            </div>

            <div class="shortcuts">
                <a class="shortcut" href="https://youtube.com">
                    <div class="shortcut-icon">▶</div>
                    <span>YouTube</span>
                </a>
                <a class="shortcut" href="https://google.com">
                    <div class="shortcut-icon">G</div>
                    <span>Google</span>
                </a>
                <a class="shortcut" href="https://reddit.com">
                    <div class="shortcut-icon">R</div>
                    <span>Reddit</span>
                </a>
                <a class="shortcut" href="https://github.com">
                    <div class="shortcut-icon">⌘</div>
                    <span>GitHub</span>
                </a>
            </div>
        </div>

        <script>
            document.getElementById('searchInput').addEventListener('keypress', function (e) {
                if (e.key === 'Enter') {
                    let query = this.value;
                    if (query) {
                        window.location.href = 'https://www.google.com/search?q=' + encodeURIComponent(query);
                    }
                }
            });
            document.getElementById('searchInput').focus();
        </script>
    </body>
    </html>
    """
