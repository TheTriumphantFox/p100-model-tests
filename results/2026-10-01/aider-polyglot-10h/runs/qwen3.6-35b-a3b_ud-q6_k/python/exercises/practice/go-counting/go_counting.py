WHITE = "W"
BLACK = "B"
EMPTY = ""

class Board:
    """Count territories of each player in a Go game

    Args:
        board (list[str]): A two-dimensional Go board
    """

    def __init__(self, board):
        self.board = board
        self.height = len(board)
        self.width = len(board[0]) if self.height > 0 else 0

    def territory(self, x, y):
        """Find the owner and the territories given a coordinate on
           the board

        Args:
            x (int): Column on the board
            y (int): Row on the board

        Returns:
            (str, set): A tuple, the first element being the owner
                        of that area.  One of "W", "B", "".  The
                        second being a set of coordinates, representing
                        the owner's territories.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise ValueError('Invalid coordinate')
        
        if self.board[y][x] != ' ':
            return ("", set())
        
        visited = set()
        stack = [(x, y)]
        visited.add((x, y))
        owner = ""
        
        while stack:
            cx, cy = stack.pop()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.board[ny][nx] == ' ':
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            stack.append((nx, ny))
                    else:
                        if owner == "":
                            owner = self.board[ny][nx]
                        elif owner != self.board[ny][nx]:
                            owner = ""
        
        return (owner, visited)

    def territories(self):
        """Find the owners and the territories of the whole board

        Args:
            none

        Returns:
            dict(str, set): A dictionary whose key being the owner
                        , i.e. "W", "B", "".  The value being a set
                        of coordinates owned by the owner.
        """
        result = {"B": set(), "W": set(), "": set()}
        visited = set()
        
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in visited and self.board[y][x] == ' ':
                    owner, territory = self.territory(x, y)
                    visited.update(territory)
                    result[owner].update(territory)
                    
        return result
