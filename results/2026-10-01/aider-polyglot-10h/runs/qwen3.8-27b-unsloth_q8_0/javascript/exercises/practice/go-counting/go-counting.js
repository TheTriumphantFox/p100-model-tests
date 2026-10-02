//
// This is only a SKELETON file for the 'Go Counting' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class GoCounting {
  constructor(board) {
    this.board = board;
    this.rows = board.length;
    this.cols = this.rows > 0 ? board[0].length : 0;
  }

  isInside(x, y) {
    return x >= 0 && x < this.cols && y >= 0 && y < this.rows;
  }

  getTerritoryAt(x, y) {
    const visited = new Set();
    const territory = [];
    const queue = [[x, y]];
    const owners = new Set();

    while (queue.length > 0) {
      const [cx, cy] = queue.shift();
      const key = `${cx},${cy}`;

      if (visited.has(key)) {
        continue;
      }
      visited.add(key);

      const cell = this.board[cy][cx];
      if (cell !== ' ') {
        if (cell === 'B' || cell === 'W') {
          owners.add(cell);
        }
        continue;
      }

      territory.push([cy, cx]);

      const neighbors = [
        [cx + 1, cy],
        [cx - 1, cy],
        [cx, cy + 1],
        [cx, cy - 1],
      ];

      for (const [nx, ny] of neighbors) {
        if (this.isInside(nx, ny) && !visited.has(`${nx},${ny}`)) {
          queue.push([nx, ny]);
        }
      }
    }

    let owner = 'NONE';
    if (owners.size === 1) {
      owner = owners.has('B') ? 'BLACK' : 'WHITE';
    }

    return {
      owner,
      territory,
    };
  }

  getTerritory(x, y) {
    if (!this.isInside(x, y)) {
      return {
        error: 'Invalid coordinate',
      };
    }

    if (this.board[y][x] !== ' ') {
      return {
        owner: 'NONE',
        territory: [],
      };
    }

    return this.getTerritoryAt(x, y);
  }

  getTerritories() {
    const territoryBlack = [];
    const territoryWhite = [];
    const territoryNone = [];
    const visited = new Set();

    for (let y = 0; y < this.rows; y++) {
      for (let x = 0; x < this.cols; x++) {
        const key = `${x},${y}`;
        if (visited.has(key) || this.board[y][x] !== ' ') {
          continue;
        }

        const { owner, territory } = this.getTerritoryAt(x, y);

        for (const [ty, tx] of territory) {
          visited.add(`${tx},${ty}`);
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

    return {
      territoryBlack,
      territoryWhite,
      territoryNone,
    };
  }
}
