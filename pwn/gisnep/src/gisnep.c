// gcc gisnep.c -o gisnep -no-pie

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void debug() {
    system("/bin/sh");
}

int hash(const char *str) {
    int acc = 0;
    for (int i = 0; str[i]; i++)
        acc += i * str[i];
    return acc;
}

void printGrid(const char *scrambled, const char *curr) {
    printf("\n");
    printf("┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐\n");
    
    int ROWS = strlen(scrambled) / 20;
    
    for (int y = 0; y < ROWS; y++) {
        for (int x = 0; x < 20; x++) {
            int i = 20 * y + x;
            int tmp = y;
            char c = ' ';
            for (int y2 = 0; y2 < ROWS; y2++)
                tmp -= scrambled[20 * y2 + x] == ' ';
            for (int y2 = 0; y2 < ROWS; y2++) {
                char c2 = scrambled[20 * y2 + x];
                if (c2 != ' ' && !tmp--) c = c2;
            }
            printf("│ %c ", c);
        }
        printf("│\n");
    }
    
    printf("╞═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╡\n");
    
    for (int y = 0; y < ROWS; y++) {
        for (int x = 0; x < 20; x++) {
            int i = 20 * y + x;
            printf(scrambled[i] == ' ' ? "│███" : "│%-3i", i + 1);
        }
        printf("│\n");

        for (int x = 0; x < 20; x++) {
            int i = 20 * y + x;
            printf(scrambled[i] == ' ' ? "│███" : "│ %c ", curr[i]);
        }
        printf("│\n");
        
        if (y < ROWS - 1)
            printf("├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤\n");
    }
    
    printf("└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘\n");
    printf("Enter position and letter (e.g. '5 A'). Use '0 X' to exit or '0 P' to print grid.\n");
}

int play(int winHash, const char *scrambled) {
    char curr[128];
    sprintf(curr, "%*s", (int)strlen(scrambled), ""); // fill with spaces
    printGrid(scrambled, curr);
    
    while (1) {
        if (winHash == hash(curr)) {
            printf("Congratulations, you solved the gisnep! The full quote is:\n");
            printf(curr);
            return 1;
        }
        
        unsigned int position;
        char letter;
        printf("> ");
        scanf("%u %c", &position, &letter);
        
        if (position == 0) {
            if (letter == 'X') return 0;
            else if (letter == 'P') printGrid(scrambled, curr);
            else printf("Invalid command!\n");
        } else if (position > strlen(scrambled) || scrambled[position - 1] == ' ')
            printf("Invalid position!\n");
        else
            curr[position - 1] = letter;
    }
}

int main() {
    setbuf(stdin, 0);
    setbuf(stdout, 0);
    setbuf(stderr, 0);
    
    while (1) {
        char line[32];
        printf("\n--------------------\n");
        printf("Pick a gisnep to play! We have quotes by various famous CTF players:\n");
        printf("genni, joseph, neobeo, superbeetlegamer, toasterpwn\n> ");
        scanf("%s", line);
        if (!strcmp(line, "exit")) break;
        else if (!strcmp(line, "genni"))            play(121346, "AALKO COOA OGE CAN I BOL YGR D QIRAPHON HESUT OUYPTSURSTIY  ");
        else if (!strcmp(line, "joseph"))           play(278995, "HEEE GHIOBA :DAD25 INH IMOJO LASAH NA HMO ENNS OTU TCKA G:MOTM OS NYU D ETEONE TWSLYT               ");
        else if (!strcmp(line, "neobeo"))           play(207070, "DO CIC BEEFEH EEUAHAN OH NTERE OIENQ IR NO ROSUPUS TRHRR TSES TYOU QXTSTTOS     ");
        else if (!strcmp(line, "superbeetlegamer")) play(199583, "AAII EC DHD GE CEDD ONOTHOM IIIINEEDII FWO TS OETN NTJNFTNON RR TSRLUTINW       ");
        else if (!strcmp(line, "toasterpwn"))       play(110113, "A ECANI EOICPH IO PHE SHIRKEJT ERYPTS TLIYTR TO SXSST       ");
        //else if (!strcmp(line, "debug")) debug();
        else printf("Unknown author!");
    }
}
