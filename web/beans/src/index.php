<?php

define('BEAN_COST', 25);

function validate_integer($s) {
    return ctype_digit(trim($s));
}

session_start();

$_SESSION['money'] ??= 100;
$_SESSION['beans'] ??= 0;

$error_msg = null;
$success_msg = null;

if (isset($_REQUEST['action'])) {
    switch ($_REQUEST['action']) {
        case 'buy':
            $amt = $_REQUEST['amt'];
            if (!validate_integer($amt)) {
                $error_msg = "That amount isn't valid!";
                break;
            }
            if ($amt < 0) {
                $error_msg = "You can't buy negative beans!";
                break;
            }
            if ($_SESSION['money'] < $amt * BEAN_COST) {
                $error_msg = "You can't afford this!";
                break;
            }
            $_SESSION['money'] -= $amt * BEAN_COST;
            $_SESSION['beans'] += $amt;
            $success_msg = "Bought $amt beans.";
            break;
        case 'sell':
            $amt = $_REQUEST['amt'];
            if (!validate_integer($amt)) {
                $error_msg = "That amount isn't valid!";
                break;
            }
            if ($amt < 0) {
                $error_msg = "You can't sell negative beans!";
                break;
            }
            if ($_SESSION['beans'] < $amt) {
                $error_msg = "You don't have that many beans to sell!";
                break;
            }
            $_SESSION['beans'] -= $amt;
            $_SESSION['money'] += $amt * BEAN_COST;
            $success_msg = "Sold $amt beans.";
            break;
        case 'flag':
            if ($_SESSION['money'] > 1337) {
                $success_msg = file_get_contents('/flag.txt');
                break;
            }
            $error_msg = "You need 1337 money for the flag!";
            break;
    }
}

?><!DOCTYPE html>
<html>
<head>
    <title>Bean Trader</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Patrick+Hand&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Patrick Hand', cursive;
            background-color: #f9f4e8;
            background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23bbb5a5' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E");
        }
        .hand-drawn {
            border: 3px solid #2d3748;
            border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
            padding: 1em;
            line-height: 1.5em;
            background-color: white;
            box-shadow: 2px 2px 0 #2d3748;
        }
        .hand-drawn-button {
            border: 2px solid #2d3748;
            border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
            padding: 0.5em 1em;
            transition: all 0.1s ease;
            background-color: #4a5568;
            color: white;
            font-family: 'Caveat', cursive;
            font-size: 1.2em;
            box-shadow: 2px 2px 0 #2d3748;
        }
        .hand-drawn-button:hover {
            transform: translate(-2px, -2px);
            box-shadow: 4px 4px 0 #2d3748;
        }
        .hand-drawn-button:active {
            transform: translate(0, 0);
            box-shadow: 0 0 0 #2d3748;
        }
        .hand-drawn-input {
            border: 2px solid #2d3748;
            border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
            padding: 0.5em;
            font-family: 'Patrick Hand', cursive;
            box-shadow: 2px 2px 0 #2d3748;
            width: 100px;
        }
        .error {
            color: #e53e3e;
            font-family: 'Caveat', cursive;
            font-size: 1.2em;
        }
        .success {
            color: #38a169;
            font-family: 'Caveat', cursive;
            font-size: 1.2em;
        }
        .title {
            font-family: 'Caveat', cursive;
            font-weight: bold;
            font-size: 2.5em;
            color: #2d3748;
            text-shadow: 2px 2px 0 #fff;
        }
    </style>
</head>
<body class="min-h-screen p-8">
    <div class="max-w-xl mx-auto">
        <h1 class="title text-center mb-8">🫘 Bean Trader 🫘</h1>
        
        <div class="hand-drawn mb-8">
            <div class="text-xl mb-4">Your Stash:</div>
            <div class="grid grid-cols-2 gap-4">
                <div>Money: $<?php echo $_SESSION['money']; ?></div>
                <div>Beans: <?php echo $_SESSION['beans']; ?></div>
            </div>
        </div>

        <?php if ($error_msg): ?>
            <div class="error hand-drawn mb-4"><?php echo $error_msg; ?></div>
        <?php endif; ?>

        <?php if ($success_msg): ?>
            <div class="success hand-drawn mb-4"><?php echo $success_msg; ?></div>
        <?php endif; ?>

        <div class="hand-drawn mb-8">
            <div class="text-xl mb-4">Trade Beans</div>
            <div class="grid grid-cols-2 gap-8">
                <form method="post" class="flex flex-col items-start gap-4">
                    <input type="hidden" name="action" value="buy">
                    <label>
                        Buy Beans:
                        <input type="number" name="amt" class="hand-drawn-input ml-2" min="0">
                    </label>
                    <button type="submit" class="hand-drawn-button">Buy ($<?php echo BEAN_COST; ?> each)</button>
                </form>

                <form method="post" class="flex flex-col items-start gap-4">
                    <input type="hidden" name="action" value="sell">
                    <label>
                        Sell Beans:
                        <input type="number" name="amt" class="hand-drawn-input ml-2" min="0">
                    </label>
                    <button type="submit" class="hand-drawn-button">Sell ($<?php echo BEAN_COST; ?> each)</button>
                </form>
            </div>
        </div>

        <form method="post" class="text-center">
            <input type="hidden" name="action" value="flag">
            <button type="submit" class="hand-drawn-button">Get Flag (costs $1337)</button>
        </form>
    </div>
</body>
</html>