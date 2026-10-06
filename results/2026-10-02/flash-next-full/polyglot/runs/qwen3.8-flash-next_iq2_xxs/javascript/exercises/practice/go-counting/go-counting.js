//
// This is only a SKELETON file for the 'Go Counting' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class GoCounting {
  constructor(board) {
    this.board = board;
    this.height = board.length;
    this.width = board[0].length;
  }

  getTerritory(x, y) {
    if (x < 0 || x >= this.width || y < 0 || y >= this.height) {
      throw new Error('Coordinate is invalid');
    }

    const cell = this.board[y][x];
    if (cell === 'B' || cell === 'W') {
      return { owner: 'NONE', territory: [] };
    }

    // Find connected empty cells starting from (x, y)
    const visited = new Set();
    const territory = [];
    const stack = [[x, y]];
    let owner = 'NONE';
    let foundBlack = false;
    let foundWhite = false;

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
          [cx - 1, cy], [cx + 1, cy], [cx, cy - 1], [cx, cy + 1]
        ];
        for (const [nx, ny] of neighbors) {
          if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height) {
            const ncell = this.board[ny][nx];
            if (ncell === ' ') {
              stack.push([nx, ny]);
            } else if (ncell === 'B') {
              foundBlack = true;
            } else if (ncell === 'W') {
              foundWhite = true;
            }
          }
        }
      }
    }

    if (foundBlack && foundWhite) {
      owner = 'NONE';
    } else if (foundBlack) {
      owner = 'BLACK';
    } else if (foundWhite) {
      owner = 'WHITE';
    } else {
      owner = 'NONE';
    }

    // Sort territory by y then x
    territory.sort((a, b) => {
      if (a[1] !== b[1]) return a[1] - b[1];
      return a[0] - b[0];
    });

    return { owner, territory };
  }

  getTerritories() {
    const visited = new Set();
    const territoryBlack = [];
    const territoryWhite = [];
    const territoryNone = [];

    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        const key = `${x},${y}`;
        if (visited.has(key)) continue;

        const cell = this.board[y][x];
        if (cell === ' ') {
          // Find connected empty cells starting from (x, y)
          const localVisited = new Set();
          const territory = [];
          const stack = [[x, y]];
          let owner = 'NONE';
          let foundBlack = false;
          let foundWhite = false;

          while (stack.length > 0) {
            const [cx, cy] = stack.pop();
            const lkey = `${cx},${cy}`;
            if (localVisited.has(lkey)) continue;
            localVisited.add(lkey);
            visited.add(lkey);

            const cell = this.board[cy][cx];
            if (cell === ' ') {
              territory.push([cx, cy]);
              // Check neighbors
              const neighbors = [
                [cx - 1, cy], [cx + 1, cy], [cx, cy - 1], [cx, cy + 1]
              ];
              for (const [nx, ny] of neighbors) {
                if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height) {
                  const ncell = this.board[ny][nx];
                  if (ncell === ' ') {
                    stack.push([nx, ny]);
                  } else if (ncell === 'B') {
                    foundBlack = true;
                  } else if (ncell === 'W') {
                    foundWhite = true;
                  }
                }
              }
            }
          }

          if (foundBlack && foundWhite) {
            owner = 'NONE';
          } else if (foundBlack) {
            owner = 'BLACK';
          } else if (foundWhite) {
            owner = 'WHITE';
          } else {
            owner = 'NONE';
          }

          // Sort the found territory group
          territory.sort((a, b) => {
            if (a[1] !== b[1]) return a[1] - b[1];
            return a[0] - b[0];
          });

          if (owner === 'BLACK') {
            territoryBlack.push(...territory);
          } else if (owner === 'WHITE') {
            territoryWhite.push(...territory);
          } else {
            territoryNone.push(...territory);
          }
        } else {
          // Mark stones as visited so they aren't processed as empty cells
          visited.add(key);
        }
      }
    }

    // Sort the final territory arrays
    const sortTerritories = (arr) => {
      arr.sort((a, b) => {
        if (a[1] !== b[1]) return a[1] - b[1];
        return a[0] - b[0];
      });
    };

    sortTerritories(territoryBlack);
    sortTerritories(territoryWhite);
    sortTerritories(territoryNone);

    return { territoryBlack, territoryWhite, territoryNone };
  }
}
