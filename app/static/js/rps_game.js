function play(playerChoice) {
    const choices = ['rock', 'paper', 'scissors'];
    const computerChoice = choices[Math.floor(Math.random() * 3)];
    const result = determineWinner(playerChoice, computerChoice);

    const playerImage = `<img src="static/image/${playerChoice}.png" alt="${playerChoice}" style="width:50px;">`;
    const computerImage = `<img src="static/image/${computerChoice}.png" alt="${computerChoice}" style="width:50px;">`;

    document.getElementById('result').innerHTML = `You chose ${playerChoice}.<br>You: ${playerImage}<br>Computer: ${computerImage}<br>${result}`;
}

function determineWinner(player, computer) {
    if (player === computer) {
        return "It's a tie!";
    } else if ((player === 'rock' && computer === 'scissors') ||
               (player === 'paper' && computer === 'rock') ||
               (player === 'scissors' && computer === 'paper')) {
        return "You win!";
    } else {
        return "You lose!";
    }
}
