// Vitrine do compilador MPL
// Programa do grupo para a Entrega 4 e para a apresentacao.
//
// A MPL nao converte numero em texto. Entao este programa comeca escrevendo
// essa conversao na propria MPL, e depois a usa para imprimir frases com
// numeros dentro: recursao, divisao inteira, resto e texto trabalhando juntos.


// ---- Numero para texto -----------------------------------------------------

funcao texto algarismo(inteiro d) {
  texto r = "0";
  se (d == 1) { r = "1"; }
  se (d == 2) { r = "2"; }
  se (d == 3) { r = "3"; }
  se (d == 4) { r = "4"; }
  se (d == 5) { r = "5"; }
  se (d == 6) { r = "6"; }
  se (d == 7) { r = "7"; }
  se (d == 8) { r = "8"; }
  se (d == 9) { r = "9"; }
  retorne r;
}

// 2026 vira emTexto(202) + "6", que vira emTexto(20) + "2" + "6", ...
funcao texto emTexto(inteiro n) {
  se (n < 0) {
    retorne "-" + emTexto(-n);
  }
  se (n < 10) {
    retorne algarismo(n);
  }
  retorne emTexto(n / 10) + algarismo(n % 10);
}

// A mesma ideia, na base 2.
funcao texto emBinario(inteiro n) {
  se (n < 2) {
    retorne algarismo(n);
  }
  retorne emBinario(n / 2) + algarismo(n % 2);
}


// ---- Torre de Hanoi ---------------------------------------------------------
// Devolve quantos movimentos fez. A variavel 'antes' precisa sobreviver a
// segunda chamada recursiva: so funciona porque cada chamada tem o seu
// proprio registro de ativacao.

funcao inteiro hanoi(inteiro discos, texto origem, texto destino, texto apoio) {
  se (discos == 0) {
    retorne 0;
  }
  inteiro antes = hanoi(discos - 1, origem, apoio, destino);
  escreva("  disco " + emTexto(discos) + ": " + origem + " -> " + destino);
  inteiro depois = hanoi(discos - 1, apoio, destino, origem);
  retorne antes + 1 + depois;
}


// ---- Raiz quadrada pelo metodo de Newton ---------------------------------------

funcao real raiz(real x) {
  real r = x;
  inteiro volta = 0;
  enquanto (volta < 20) {
    r = (r + x / r) / 2;
    volta = volta + 1;
  }
  retorne r;
}


// ---- O programa -------------------------------------------------------------

funcao vazio principal() {
  escreva("== Numeros que viram texto ==");
  escreva("o ano " + emTexto(2026) + " em binario e " + emBinario(2026));

  escreva("");
  escreva("== Torre de Hanoi com 3 discos ==");
  inteiro movimentos = hanoi(3, "A", "C", "B");
  escreva("total: " + emTexto(movimentos) + " movimentos");

  escreva("");
  escreva("== As armadilhas da divisao ==");
  escreva("7 / 2 = " + emTexto(7 / 2));
  escreva("-7 / 2 = " + emTexto(-7 / 2));
  escreva("-7 % 3 = " + emTexto(-7 % 3));
  real metade = 7 / 2;
  escreva("real metade = 7 / 2 guarda:");
  escreva(metade);
  escreva("ja 7 / 2.0 vale:");
  escreva(7 / 2.0);

  escreva("");
  escreva("== Raiz quadrada por Newton ==");
  escreva("raiz de 2:");
  escreva(raiz(2));
  escreva("raiz de 10:");
  escreva(raiz(10));
}