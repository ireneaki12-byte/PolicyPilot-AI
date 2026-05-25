from flask import Flask, request, jsonify, render_template_string, url_for
from app.rag_pipeline import answer_question

app = Flask(__name__)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PolicyPilot AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        :root {
            --magenta: #E20177;
            --deep-magenta: #B00065;
            --purple: #A9218E;
            --yellow: #FFDD00;
            --blue: #00AEEF;
            --green: #A6CE39;
            --sky: #BFE8F7;
            --dark: #1A0715;
            --dark-2: #260D20;
            --dark-3: #37122E;
            --text: #FFF7FC;
            --muted: #D8A9C4;
            --white: #FFFFFF;
        }

        html,
        body {
            min-height: 100%;
        }

        body {
            font-family: 'DM Sans', sans-serif;
            background:
                radial-gradient(circle at top left, rgba(255, 221, 0, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(0, 174, 239, 0.16), transparent 30%),
                linear-gradient(135deg, var(--magenta), var(--purple) 50%, var(--dark));
            color: var(--text);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 24px;
            overflow: hidden;
        }

        .app-shell {
            width: min(1180px, 100%);
            height: min(720px, calc(100vh - 48px));
            min-height: 560px;
            background: rgba(26, 7, 21, 0.94);
            border-radius: 28px;
            overflow: hidden;
            display: grid;
            grid-template-columns: 300px minmax(0, 1fr);
            box-shadow: 0 30px 90px rgba(0, 0, 0, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.16);
        }

        .sidebar {
            background:
                linear-gradient(180deg, rgba(226, 1, 119, 0.22), rgba(26, 7, 21, 0.96)),
                var(--dark-2);
            border-right: 1px solid rgba(255, 255, 255, 0.12);
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
            min-width: 0;
        }

        .sidebar::before {
            content: "";
            position: absolute;
            width: 240px;
            height: 240px;
            background: var(--yellow);
            border-radius: 50%;
            opacity: 0.08;
            top: -90px;
            left: -80px;
        }

        .brand {
            padding: 24px 22px 18px;
            position: relative;
            z-index: 1;
        }

        .brand-row {
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 0;
        }

        .brand-icon {
            width: 44px;
            height: 44px;
            border-radius: 16px;
            background: linear-gradient(135deg, var(--yellow), #FF9B21);
            color: var(--purple);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 23px;
            box-shadow: 0 10px 25px rgba(255, 221, 0, 0.25);
            flex-shrink: 0;
        }

        .brand-name {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 22px;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: white;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .brand-tagline {
            margin-top: 8px;
            font-size: 12px;
            color: var(--muted);
            padding-left: 56px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .mascot-card {
            margin: 10px 18px 18px;
            border-radius: 24px;
            padding: 16px;
            position: relative;
            overflow: hidden;
            min-height: 240px;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            background:
                radial-gradient(circle at top right, rgba(255, 221, 0, 0.22), transparent 28%),
                radial-gradient(circle at bottom left, rgba(226, 1, 119, 0.22), transparent 35%),
                linear-gradient(180deg, rgba(191, 232, 247, 0.94), rgba(255, 255, 255, 0.92));
            box-shadow: inset 0 -18px 40px rgba(226, 1, 119, 0.18);
        }

        .mascot-card::after {
            content: "";
            position: absolute;
            right: -40px;
            bottom: -40px;
            width: 160px;
            height: 160px;
            border-radius: 50%;
            background: rgba(226, 1, 119, 0.16);
        }

        .speech {
            position: absolute;
            right: 12px;
            top: 16px;
            width: 138px;
            background: var(--magenta);
            color: white;
            border-radius: 18px;
            padding: 12px 13px;
            font-size: 12px;
            line-height: 1.35;
            box-shadow: 0 8px 22px rgba(169, 33, 142, 0.3);
            z-index: 3;
        }

        .speech strong {
            color: var(--yellow);
        }

        .katibu-gif {
            width: 190px;
            height: auto;
            object-fit: contain;
            position: absolute;
            left: 22px;
            bottom: -6px;
            z-index: 2;
            filter: drop-shadow(0 18px 24px rgba(169, 33, 142, 0.25));
        }

        .section-label {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--yellow);
            letter-spacing: 1.2px;
            padding: 8px 22px;
        }

        .policy-list {
            padding: 0 14px;
            flex: 1;
            overflow-y: auto;
            min-height: 0;
        }

        .policy-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 11px 12px;
            margin-bottom: 7px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.055);
            border: 1px solid rgba(255, 255, 255, 0.08);
            min-width: 0;
        }

        .policy-item.active {
            background: rgba(226, 1, 119, 0.22);
            border-color: rgba(255, 221, 0, 0.4);
        }

        .policy-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            flex-shrink: 0;
        }

        .policy-name {
            font-size: 13px;
            color: #F7DCEC;
            flex: 1;
            min-width: 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .policy-count {
            font-size: 10px;
            font-weight: 700;
            color: var(--dark);
            background: var(--yellow);
            padding: 3px 8px;
            border-radius: 999px;
            flex-shrink: 0;
        }

        .sidebar-footer {
            padding: 18px 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.12);
            font-size: 12px;
            color: var(--muted);
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 7px 10px;
            border-radius: 999px;
            background: rgba(166, 206, 57, 0.12);
            color: var(--green);
            font-weight: 600;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--green);
            border-radius: 50%;
            box-shadow: 0 0 0 4px rgba(166, 206, 57, 0.15);
        }

        .chat-main {
            display: flex;
            flex-direction: column;
            min-width: 0;
            min-height: 0;
            background:
                radial-gradient(circle at top right, rgba(255, 221, 0, 0.08), transparent 28%),
                var(--dark);
        }

        .chat-header {
            padding: 20px 24px;
            background: rgba(38, 13, 32, 0.98);
            border-bottom: 1px solid rgba(255, 255, 255, 0.11);
            display: flex;
            align-items: center;
            gap: 14px;
            flex-shrink: 0;
            min-width: 0;
        }

        .katibu-avatar {
            width: 54px;
            height: 54px;
            border-radius: 18px;
            background: var(--sky);
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(255, 221, 0, 0.75);
            flex-shrink: 0;
        }

        .katibu-avatar img {
            width: 66px;
            height: 66px;
            object-fit: contain;
            transform: translateY(8px);
        }

        .header-title {
            flex: 1;
            min-width: 0;
        }

        .header-title h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 23px;
            letter-spacing: -0.6px;
            color: var(--white);
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .header-title p {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.35;
        }

        .header-chip {
            background: rgba(255, 221, 0, 0.12);
            color: var(--yellow);
            border: 1px solid rgba(255, 221, 0, 0.28);
            padding: 8px 13px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            white-space: nowrap;
            flex-shrink: 0;
        }

        .messages {
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 18px;
        }

        .messages::-webkit-scrollbar,
        .policy-list::-webkit-scrollbar,
        .suggestions::-webkit-scrollbar {
            width: 5px;
            height: 4px;
        }

        .messages::-webkit-scrollbar-thumb,
        .policy-list::-webkit-scrollbar-thumb,
        .suggestions::-webkit-scrollbar-thumb {
            background: rgba(255, 221, 0, 0.25);
            border-radius: 999px;
        }

        .welcome-panel {
            background:
                linear-gradient(135deg, rgba(226, 1, 119, 0.18), rgba(169, 33, 142, 0.14)),
                rgba(255, 255, 255, 0.055);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 24px;
            padding: 20px;
            display: grid;
            grid-template-columns: minmax(0, 1fr) 150px;
            gap: 16px;
            align-items: center;
        }

        .welcome-panel h2 {
            font-family: 'Space Grotesk', sans-serif;
            color: white;
            font-size: 22px;
            margin-bottom: 8px;
        }

        .welcome-panel p {
            color: #EACDDD;
            font-size: 14px;
            line-height: 1.55;
        }

        .welcome-katibu-gif {
            width: 140px;
            height: auto;
            object-fit: contain;
            justify-self: center;
            filter: drop-shadow(0 20px 30px rgba(0, 0, 0, 0.25));
        }

        .msg-row {
            display: flex;
            gap: 11px;
            align-items: flex-end;
        }

        .msg-row.user {
            flex-direction: row-reverse;
        }

        .msg-avatar {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            font-size: 12px;
            font-weight: 800;
        }

        .msg-avatar.ai {
            background: var(--sky);
            border: 1px solid rgba(255, 221, 0, 0.6);
        }

        .msg-avatar.ai img {
            width: 48px;
            height: 48px;
            object-fit: contain;
            transform: translateY(6px);
        }

        .msg-avatar.user-av {
            background: linear-gradient(135deg, var(--green), var(--blue));
            color: #061B22;
        }

        .msg-body {
            max-width: min(78%, 720px);
            display: flex;
            flex-direction: column;
            gap: 6px;
            min-width: 0;
        }

        .msg-row.user .msg-body {
            align-items: flex-end;
        }

        .msg-bubble {
            padding: 13px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.58;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }

        .msg-bubble.ai {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #F4DFEB;
            border-bottom-left-radius: 5px;
        }

        .msg-bubble.user-b {
            background: linear-gradient(135deg, var(--magenta), var(--purple));
            color: white;
            border-bottom-right-radius: 5px;
            box-shadow: 0 12px 28px rgba(226, 1, 119, 0.24);
        }

        .msg-time {
            font-size: 10px;
            color: var(--muted);
            padding: 0 5px;
        }

        .source-card {
            margin-top: 8px;
            background: rgba(38, 13, 32, 0.92);
            border: 1px solid rgba(0, 174, 239, 0.22);
            border-radius: 16px;
            padding: 12px 14px;
            overflow-wrap: anywhere;
        }

        .source-title {
            font-family: 'Space Grotesk', sans-serif;
            color: var(--yellow);
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .source-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .source-item {
            font-size: 12px;
            color: #D8B8CB;
            line-height: 1.45;
            border-left: 3px solid var(--blue);
            padding-left: 9px;
        }

        .suggestions {
            padding: 10px 24px 4px;
            display: flex;
            gap: 10px;
            overflow-x: auto;
            flex-shrink: 0;
            -webkit-overflow-scrolling: touch;
        }

        .suggest-btn {
            white-space: nowrap;
            border: 1px solid rgba(255, 221, 0, 0.22);
            background: rgba(255, 221, 0, 0.08);
            color: var(--yellow);
            padding: 9px 14px;
            border-radius: 999px;
            cursor: pointer;
            font-family: 'DM Sans', sans-serif;
            font-size: 12px;
            font-weight: 700;
            transition: 0.18s ease;
            flex-shrink: 0;
        }

        .suggest-btn:hover {
            background: rgba(226, 1, 119, 0.22);
            color: white;
            border-color: rgba(226, 1, 119, 0.5);
        }

        .input-bar {
            padding: 16px 22px 22px;
            background: rgba(38, 13, 32, 0.98);
            border-top: 1px solid rgba(255, 255, 255, 0.11);
            flex-shrink: 0;
        }

        .input-wrap {
            display: flex;
            align-items: flex-end;
            gap: 10px;
            background: rgba(55, 18, 46, 0.95);
            border: 1px solid rgba(255, 221, 0, 0.25);
            border-radius: 20px;
            padding: 12px;
        }

        .input-wrap:focus-within {
            border-color: var(--yellow);
            box-shadow: 0 0 0 4px rgba(255, 221, 0, 0.08);
        }

        textarea {
            flex: 1;
            border: none;
            outline: none;
            background: transparent;
            color: var(--text);
            resize: none;
            min-height: 28px;
            max-height: 100px;
            font-size: 14px;
            line-height: 1.5;
            font-family: 'DM Sans', sans-serif;
            min-width: 0;
        }

        textarea::placeholder {
            color: #B98CA7;
        }

        .send-btn {
            width: 42px;
            height: 42px;
            border: none;
            border-radius: 14px;
            background: linear-gradient(135deg, var(--yellow), #FF9B21);
            color: var(--purple);
            font-size: 18px;
            font-weight: 900;
            cursor: pointer;
            flex-shrink: 0;
            box-shadow: 0 12px 24px rgba(255, 221, 0, 0.18);
        }

        .send-btn:hover {
            transform: translateY(-1px);
            opacity: 0.95;
        }

        .typing {
            display: none;
            align-items: center;
            gap: 5px;
            padding: 11px 15px;
            width: fit-content;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            border-bottom-left-radius: 5px;
        }

        .typing span {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--yellow);
            animation: bounce 1s infinite;
        }

        .typing span:nth-child(2) {
            animation-delay: 0.2s;
            background: var(--magenta);
        }

        .typing span:nth-child(3) {
            animation-delay: 0.4s;
            background: var(--blue);
        }

        @keyframes bounce {
            0%, 70%, 100% {
                transform: translateY(0);
                opacity: 0.45;
            }
            35% {
                transform: translateY(-5px);
                opacity: 1;
            }
        }

        /* Tablet */
        @media (max-width: 1024px) {
            body {
                padding: 14px;
            }

            .app-shell {
                height: calc(100vh - 28px);
                grid-template-columns: 260px minmax(0, 1fr);
            }

            .brand {
                padding: 20px 18px 14px;
            }

            .brand-name {
                font-size: 18px;
            }

            .brand-tagline {
                font-size: 10.5px;
                padding-left: 52px;
            }

            .mascot-card {
                min-height: 205px;
                margin-left: 14px;
                margin-right: 14px;
            }

            .katibu-gif {
                width: 160px;
                left: 14px;
            }

            .speech {
                width: 120px;
                font-size: 11px;
            }

            .policy-item {
                padding: 10px;
            }

            .msg-body {
                max-width: 84%;
            }
        }

        /* Mobile */
        @media (max-width: 760px) {
            body {
                padding: 0;
                align-items: stretch;
                overflow: hidden;
            }

            .app-shell {
                width: 100%;
                height: 100dvh;
                min-height: 0;
                border-radius: 0;
                grid-template-columns: 1fr;
                border: none;
            }

            .sidebar {
                display: none;
            }

            .chat-main {
                height: 100dvh;
            }

            .chat-header {
                padding: 14px 16px;
                gap: 10px;
            }

            .katibu-avatar {
                width: 44px;
                height: 44px;
                border-radius: 14px;
            }

            .katibu-avatar img {
                width: 56px;
                height: 56px;
                transform: translateY(7px);
            }

            .header-title h1 {
                font-size: 18px;
            }

            .header-title p {
                font-size: 11.5px;
                line-height: 1.25;
            }

            .header-chip {
                display: none;
            }

            .messages {
                padding: 16px 14px;
                gap: 14px;
            }

            .welcome-panel {
                grid-template-columns: 1fr;
                padding: 16px;
                border-radius: 20px;
            }

            .welcome-panel h2 {
                font-size: 18px;
            }

            .welcome-panel p {
                font-size: 13px;
            }

            .welcome-katibu-gif {
                display: none;
            }

            .msg-avatar {
                width: 30px;
                height: 30px;
            }

            .msg-avatar.ai img {
                width: 42px;
                height: 42px;
                transform: translateY(6px);
            }

            .msg-body {
                max-width: 88%;
            }

            .msg-bubble {
                font-size: 13px;
                padding: 11px 13px;
                border-radius: 16px;
            }

            .source-card {
                padding: 10px 12px;
                border-radius: 14px;
            }

            .source-title {
                font-size: 12px;
            }

            .source-item {
                font-size: 11.5px;
            }

            .suggestions {
                padding: 8px 14px 4px;
                gap: 8px;
            }

            .suggest-btn {
                font-size: 11.5px;
                padding: 8px 12px;
            }

            .input-bar {
                padding: 12px 12px 14px;
            }

            .input-wrap {
                border-radius: 18px;
                padding: 10px;
            }

            textarea {
                font-size: 13px;
            }

            .send-btn {
                width: 38px;
                height: 38px;
                border-radius: 13px;
                font-size: 16px;
            }
        }

        /* Small phones */
        @media (max-width: 420px) {
            .chat-header {
                padding: 12px;
            }

            .katibu-avatar {
                width: 40px;
                height: 40px;
            }

            .katibu-avatar img {
                width: 52px;
                height: 52px;
            }

            .header-title h1 {
                font-size: 16px;
            }

            .header-title p {
                font-size: 10.5px;
            }

            .messages {
                padding: 12px 10px;
            }

            .welcome-panel {
                padding: 14px;
            }

            .welcome-panel h2 {
                font-size: 16px;
            }

            .welcome-panel p {
                font-size: 12px;
            }

            .msg-body {
                max-width: 92%;
            }

            .msg-bubble {
                font-size: 12.5px;
                padding: 10px 12px;
            }

            .suggestions {
                padding-left: 10px;
                padding-right: 10px;
            }

            .suggest-btn {
                font-size: 11px;
                padding: 7px 10px;
            }

            .input-bar {
                padding: 10px;
            }

            .send-btn {
                width: 36px;
                height: 36px;
            }
        }
    </style>
</head>

<body>
    <div class="app-shell">

        <aside class="sidebar">
            <div class="brand">
                <div class="brand-row">
                    <div class="brand-icon">✈</div>
                    <div class="brand-name">PolicyPilot AI</div>
                </div>
                <div class="brand-tagline">Aviation Policy Assistant</div>
            </div>

            <div class="mascot-card">
                <div class="speech">
                    Hi, I’m <strong>Katibu</strong>. Ask me about your policies.
                </div>

                <img
                    src="{{ katibu_gif_url }}"
                    alt="Katibu waving hello"
                    class="katibu-gif"
                >
            </div>

            <div class="section-label">Policy Corpus</div>

            <div class="policy-list">
                <div class="policy-item active">
                    <div class="policy-dot" style="background:#E20177"></div>
                    <div class="policy-name">Data Protection Policy</div>
                    <div class="policy-count">Core</div>
                </div>

                <div class="policy-item">
                    <div class="policy-dot" style="background:#FFDD00"></div>
                    <div class="policy-name">Website Privacy Policy</div>
                    <div class="policy-count">Web</div>
                </div>

                <div class="policy-item">
                    <div class="policy-dot" style="background:#00AEEF"></div>
                    <div class="policy-name">Privacy Policy</div>
                    <div class="policy-count">Cust</div>
                </div>

                <div class="policy-item">
                    <div class="policy-dot" style="background:#A6CE39"></div>
                    <div class="policy-name">Cookie Policy</div>
                    <div class="policy-count">Web</div>
                </div>

                <div class="policy-item">
                    <div class="policy-dot" style="background:#A9218E"></div>
                    <div class="policy-name">Data Retention Policy</div>
                    <div class="policy-count">Ops</div>
                </div>

                <div class="policy-item">
                    <div class="policy-dot" style="background:#E20177"></div>
                    <div class="policy-name">Data Subject Rights Policy</div>
                    <div class="policy-count">DSR</div>
                </div>

                <div class="policy-item">
                    <div class="policy-dot" style="background:#FFDD00"></div>
                    <div class="policy-name">Data Breach Procedures</div>
                    <div class="policy-count">IR</div>
                </div>
            </div>

            <div class="sidebar-footer">
                <div class="status-pill">
                    <span class="status-dot"></span>
                    RAG assistant online
                </div>
            </div>
        </aside>

        <main class="chat-main">
            <header class="chat-header">
                <div class="katibu-avatar">
                    <img src="{{ katibu_gif_url }}" alt="Katibu waving hello">
                </div>

                <div class="header-title">
                    <h1>PolicyPilot AI</h1>
                    <p>Ask questions about Kenya Aviation Limited policies and procedures</p>
                </div>

                <div class="header-chip">Grounded answers + citations</div>
            </header>

            <section class="messages" id="messages">
                <div class="welcome-panel">
                    <div>
                        <h2>Welcome aboard 👋</h2>
                        <p>
                            I’m <strong>PolicyPilot AI</strong>, guided by Katibu. I can help you understand policy requirements on data protection,
                            privacy, cookies, data retention, data subject rights, and breach response.
                        </p>
                    </div>
                    <img src="{{ katibu_gif_url }}" alt="Katibu waving hello" class="welcome-katibu-gif">
                </div>

                <div class="msg-row">
                    <div class="msg-avatar ai">
                        <img src="{{ katibu_gif_url }}" alt="Katibu">
                    </div>
                    <div class="msg-body">
                        <div class="msg-bubble ai">
Hello! Ask me a policy question and I’ll respond using the policy corpus, including citations and supporting snippets where available.
                        </div>
                        <div class="msg-time">PolicyPilot AI</div>
                    </div>
                </div>

                <div class="msg-row" id="typingRow" style="display:none;">
                    <div class="msg-avatar ai">
                        <img src="{{ katibu_gif_url }}" alt="Katibu">
                    </div>
                    <div class="msg-body">
                        <div class="typing" id="typingBubble">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                </div>
            </section>

            <section class="suggestions">
                <button class="suggest-btn" onclick="useSuggestion('What should an employee do if they suspect a personal data breach?')">Breach reporting</button>
                <button class="suggest-btn" onclick="useSuggestion('What are the rights of a data subject?')">Data subject rights</button>
                <button class="suggest-btn" onclick="useSuggestion('How long should a data breach record be kept?')">Retention</button>
                <button class="suggest-btn" onclick="useSuggestion('What types of cookies does the website use?')">Cookies</button>
                <button class="suggest-btn" onclick="useSuggestion('Can employees share passwords?')">Password rules</button>
            </section>

            <footer class="input-bar">
                <div class="input-wrap">
                    <textarea id="questionInput" rows="1" placeholder="Ask Katibu about a policy..." oninput="autoResize(this)"></textarea>
                    <button class="send-btn" onclick="sendQuestion()" title="Send">➜</button>
                </div>
            </footer>
        </main>
    </div>

    <script>
        const messages = document.getElementById("messages");
        const input = document.getElementById("questionInput");
        const typingRow = document.getElementById("typingRow");
        const typingBubble = document.getElementById("typingBubble");

        function autoResize(el) {
            el.style.height = "auto";
            el.style.height = Math.min(el.scrollHeight, 100) + "px";
        }

        function escapeHtml(text) {
            const div = document.createElement("div");
            div.innerText = text || "";
            return div.innerHTML;
        }

        function scrollToBottom() {
            messages.scrollTop = messages.scrollHeight;
        }

        function addUserMessage(text) {
            const row = document.createElement("div");
            row.className = "msg-row user";
            row.innerHTML = `
                <div class="msg-avatar user-av">YOU</div>
                <div class="msg-body">
                    <div class="msg-bubble user-b">${escapeHtml(text)}</div>
                    <div class="msg-time">You</div>
                </div>
            `;
            messages.insertBefore(row, typingRow);
            scrollToBottom();
        }

        function addAIMessage(data) {
            const answer = data.answer || "I could not generate an answer.";
            let sourcesHtml = "";

            if (data.citations && data.citations.length > 0) {
                sourcesHtml += `
                    <div class="source-card">
                        <div class="source-title">Sources retrieved</div>
                        <div class="source-list">
                `;

                data.citations.forEach((citation, index) => {
                    const title = citation.title || "Unknown title";
                    const source = citation.source || "Unknown source";
                    const snippet = data.snippets && data.snippets[index] ? data.snippets[index] : "";

                    sourcesHtml += `
                        <div class="source-item">
                            <strong>${escapeHtml(title)}</strong><br>
                            ${escapeHtml(source)}<br>
                            <em>${escapeHtml(snippet.substring(0, 220))}${snippet.length > 220 ? "..." : ""}</em>
                        </div>
                    `;
                });

                sourcesHtml += `
                        </div>
                    </div>
                `;
            }

            const row = document.createElement("div");
            row.className = "msg-row";
            row.innerHTML = `
                <div class="msg-avatar ai">
                    <img src="{{ katibu_gif_url }}" alt="Katibu">
                </div>
                <div class="msg-body">
                    <div class="msg-bubble ai">${escapeHtml(answer)}</div>
                    ${sourcesHtml}
                    <div class="msg-time">PolicyPilot AI · Katibu</div>
                </div>
            `;

            messages.insertBefore(row, typingRow);
            scrollToBottom();
        }

        function showTyping(show) {
            typingRow.style.display = show ? "flex" : "none";
            typingBubble.style.display = show ? "flex" : "none";
            scrollToBottom();
        }

        async function sendQuestion() {
            const question = input.value.trim();

            if (!question) {
                return;
            }

            addUserMessage(question);
            input.value = "";
            input.style.height = "auto";
            showTyping(true);

            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ question })
                });

                const data = await response.json();
                showTyping(false);

                if (!response.ok) {
                    addAIMessage({
                        answer: data.error || "Something went wrong while processing your question.",
                        citations: [],
                        snippets: []
                    });
                    return;
                }

                addAIMessage(data);

            } catch (error) {
                showTyping(false);
                addAIMessage({
                    answer: "I could not reach the PolicyPilot AI service. Please check that the Flask server is running.",
                    citations: [],
                    snippets: []
                });
            }
        }

        function useSuggestion(question) {
            input.value = question;
            autoResize(input);
            input.focus();
        }

        input.addEventListener("keydown", function(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendQuestion();
            }
        });

        scrollToBottom();
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    katibu_url = url_for("static", filename="katibu.png")
    katibu_gif_url = url_for("static", filename="media/katibu_bird_waving_hi.gif")

    return render_template_string(
        HTML_TEMPLATE,
        katibu_url=katibu_url,
        katibu_gif_url=katibu_gif_url
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    result = answer_question(question)
    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "app": "PolicyPilot AI",
    })


if __name__ == "__main__":
    app.run(debug=True)