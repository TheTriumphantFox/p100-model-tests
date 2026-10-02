class Board:
    """Count territories of each player in a Go game

    Args:
        board (list[str]): A two-dimensional Go board
    """

    def __init__(self, board):
        self.board = [list(row) for row in board]
        self.height = len(self.board)
        self.width = len(self.board[0]) if self.height > 0 else 0

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
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError('Invalid coordinate')

        if self.board[y][x] in ("W", "B"):
            return (self.board[y][x], set())

        territory = set()
        owners = set()
        stack = [(x, y)]
        visited = set()

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            territory.add((cx, cy))

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbor = self.board[ny][nx]
                    if neighbor == "":
                        if (nx, ny) not in visited:
                            stack.append((nx, ny))
                    elif neighbor in ("W", "B"):
                        owners.add(neighbor)

        if len(owners) == 1:
            owner = owners.pop()
        else:
            owner = ""

        return (owner, territory)

    def territories(self):
        """Find the owners and the territories of the whole board

        Args:
            none

        Returns:
            dict(str, set): A dictionary whose key being the owner
                        , i.e. "W", "B", "".  The value being a set
                        of coordinates owned by the owner.
        """
        result = {"W": set(), "B": set(), "": set()}
        visited = set()

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in visited:
                    owner, territory = self.territory(x, y)
                    result[owner].update(territory)
                    visited.update(territory)

        return result


WHITE = "W"
BLACK = "B"
NONE = ""
