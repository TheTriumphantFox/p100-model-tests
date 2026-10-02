//
// This is only a SKELETON file for the 'Go Counting' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class GoCounting {
  constructor(board) {
    this.board = board.map((row) => row.split(''));
    this.rows = this.board.length;
    this.cols = this.rows > 0 ? this.board[0].length : 0;
  }

  getTerritory(x, y) {
    if (x < 0 || x >= this.cols || y < 0 || y >= this.rows) {
      throw new Error('Invalid');
    }

    if (this.board[y][x] !== ' ') {
      return {
        owner: 'NONE',
        territory: [],
      };
    }

    const visited = new Set();
    const territory = [];
    const owners = new Set();
    const stack = [[x, y]];

    while (stack.length > 0) {
      const [cx, cy] = stack.pop();
      const key = `${cx},${cy}`;

      if (visited.has(key)) continue;
      visited.add(key);

      const cell = this.board[cy][cx];

      if (cell === ' ') {
        territory.push([cx, cy]);

        // Check neighbors
        const neighbors = [
          [cx - 1, cy],
          [cx + 1, cy],
          [cx, cy - 1],
          [cx, cy + 1],
        ];

        for (const [nx, ny] of neighbors) {
          if (nx >= 0 && nx < this.cols && ny >= 0 && ny < this.rows) {
            const nKey = `${nx},${ny}`;
            if (!visited.has(nKey)) {
              const nCell = this.board[ny][nx];
              if (nCell === ' ') {
                stack.push([nx, ny]);
              } else {
                owners.add(nCell);
              }
            }
          }
        }
      }
    }

    let owner = 'NONE';
    if (owners.size === 1) {
      owner = owners.has('B') ? 'BLACK' : 'WHITE';
    }

    return {
      owner,
      territory: territory.sort((a, b) => a[0] - b[0] || a[1] - b[1]),
    };
  }

  getTerritories() {
    const territoryBlack = [];
    const territoryWhite = [];
    const territoryNone = [];
    const visited = new Set();

    for (let y = 0; y < this.rows; y++) {
      for (let x = 0; x < this.cols; x++) {
        const key = `${x},${y}`;
        if (!visited.has(key) && this.board[y][x] === ' ') {
          const { territory, owner } = this.getTerritory(x, y);
          for (const coord of territory) {
            visited.add(`${coord[0]},${coord[1]}`);
          }

          if (owner === 'BLACK') {
            territoryBlack.push(...territory);
          } else if (owner === 'WHITE') {
            territoryWhite.push(...territory);
          } else {
            territoryNone.push(...territory);
          }
        }
      }
    }

    return {
      territoryBlack: territoryBlack.sort((a, b) => a[0] - b[0] || a[1] - b[1]),
      territoryWhite: territoryWhite.sort((a, b) => a[0] - b[0] || a[1] - b[1]),
      territoryNone: territoryNone.sort((a, b) => a[0] - b[0] || a[1] - b[1]),
    };
  }
}
