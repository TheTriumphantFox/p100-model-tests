//
// This is only a SKELETON file for the 'Go Counting' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class GoCounting {
  constructor(board) {
    this.board = board;
    this.height = board.length;
    this.width = this.height > 0 ? board[0].length : 0;
  }

  getTerritory(x, y) {
    if (x < 0 || x >= this.width || y < 0 || y >= this.height) {
      return { error: 'Invalid coordinate' };
    }

    const cell = this.board[y][x];
    if (cell === 'B' || cell === 'W') {
      return { owner: 'NONE', territory: [] };
    }

    const territory = [];
    const visited = new Set();
    const queue = [[x, y]];
    visited.add(`${x},${y}`);
    
    let ownerBlack = false;
    let ownerWhite = false;

    while (queue.length > 0) {
      const [cx, cy] = queue.shift();
      territory.push([cx, cy]);

      const neighbors = [
        [cx - 1, cy],
        [cx + 1, cy],
        [cx, cy - 1],
        [cx, cy + 1]
      ];

      for (const [nx, ny] of neighbors) {
        if (nx < 0 || nx >= this.width || ny < 0 || ny >= this.height) {
          continue;
        }

        const neighborCell = this.board[ny][nx];
        if (neighborCell === 'B') {
          ownerBlack = true;
        } else if (neighborCell === 'W') {
          ownerWhite = true;
        } else if (neighborCell === ' ') {
          const key = `${nx},${ny}`;
          if (!visited.has(key)) {
            visited.add(key);
            queue.push([nx, ny]);
          }
        }
      }
    }

    let owner = 'NONE';
    if (ownerBlack && !ownerWhite) {
      owner = 'BLACK';
    } else if (ownerWhite && !ownerBlack) {
      owner = 'WHITE';
    }

    // Sort territory coordinates for consistent output
    territory.sort((a, b) => {
      if (a[0] !== b[0]) return a[0] - b[0];
      return a[1] - b[1];
    });

    return { owner, territory };
  }

  getTerritories() {
    const territoryBlack = [];
    const territoryWhite = [];
    const territoryNone = [];
    const visited = new Set();

    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        if (this.board[y][x] === ' ' && !visited.has(`${x},${y}`)) {
          const result = this.getTerritory(x, y);
          
          result.territory.forEach(([tx, ty]) => {
            visited.add(`${tx},${ty}`);
          });

          if (result.owner === 'BLACK') {
            territoryBlack.push(result.territory);
          } else if (result.owner === 'WHITE') {
            territoryWhite.push(result.territory);
          } else {
            territoryNone.push(result.territory);
          }
        }
      }
    }

    return {
      territoryBlack,
      territoryWhite,
      territoryNone
    };
  }
}
