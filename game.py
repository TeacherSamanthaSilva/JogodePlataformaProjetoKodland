# Dentro da função update(), substitua a parte de game_over e victory por:

# Verificar bandeira (vitória)
if alien.colliderect(flag) and not victory:
    victory = True
    sounds.musica.stop()  # Para música de fundo
    sounds.victory.play()  # Toca som de vitória

# Inimigos e colisão com alien
for enemy in list(enemies):
    enemy.x -= enemy.speed
    if enemy.x < -50:
        enemies.remove(enemy)
        score += 1
    elif alien.colliderect(enemy):
        lives -= 1
        enemies.remove(enemy)
        if lives <= 0 and not game_over:
            game_over = True
            sounds.musica.stop()  # Para música de fundo
            sounds.gameover.play()  # Toca som de game over

# Abelhas e colisão com alien
for bee in bees:
    bee.x -= bee.speed
    bee.y += math.sin(bee.oscillation) * 2
    bee.oscillation += 0.1
    if bee.x < -50:
        bees.remove(bee)
    elif alien.colliderect(bee):
        lives -= 1
        bees.remove(bee)
        if lives <= 0 and not game_over:
            game_over = True
            sounds.musica.stop()  # Para música de fundo
            sounds.gameover.play()  # Toca som de game over
