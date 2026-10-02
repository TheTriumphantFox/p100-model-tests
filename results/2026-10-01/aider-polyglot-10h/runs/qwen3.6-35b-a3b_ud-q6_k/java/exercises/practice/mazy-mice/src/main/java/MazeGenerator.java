import java.util.Random;

public class MazeGenerator {

    private char[][] maze;

    public char[][] generatePerfectMaze(int rows, int columns) {
        return generatePerfectMaze(rows, columns, new Random().nextLong());
    }

    public char[][] generatePerfectMaze(int rows, int columns, long seed) {
        if (rows < 5 || rows > 100 || columns < 5 || columns > 100) {
            throw new IllegalArgumentException("Maze dimensions must be between 5 and 100 cells.");
        }

        int height = 2 * rows + 1;
        int width = 2 * columns + 1;
        maze = new char[height][width];

        // Initialize with walls
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                maze[y][x] = ' ';
            }
        }

        // Fill walls
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                if (y % 2 == 0 && x % 2 == 0) {
                    maze[y][x] = '┼';
                } else if (y % 2 == 0) {
                    maze[y][x] = '─';
                } else if (x % 2 == 0) {
                    maze[y][x] = '│';
                } else {
                    maze[y][x] = ' ';
                }
            }
        }

        // Carve maze using Recursive Backtracker
        Random random = new Random(seed);
        boolean[][] visited = new boolean[rows][columns];
        carveMaze(0, 0, rows, columns, visited, random);

        // Set entrance and exit
        // Entrance at left, middle-ish row (2*rows - 1)
        maze[2 * rows - 1][0] = '⇨';
        // Exit at right, row 1
        maze[1][2 * columns] = '⇨';

        // Ensure entrance and exit passages are open
        maze[2 * rows - 1][1] = ' ';
        maze[1][2 * columns - 1] = ' ';

        return maze;
    }

    private void carveMaze(int x, int y, int rows, int columns, boolean[][] visited, Random random) {
        visited[y][x] = true;

        int[] dx = {1, -1, 0, 0};
        int[] dy = {0, 0, 1, -1};
        
        // Shuffle directions
        Integer[] indices = {0, 1, 2, 3};
        for (int i = indices.length - 1; i > 0; i--) {
            int j = random.nextInt(i + 1);
            int temp = indices[i];
            indices[i] = indices[j];
            indices[j] = temp;
        }

        for (int i : indices) {
            int nx = x + dx[i];
            int ny = y + dy[i];

            if (nx >= 0 && nx < columns && ny >= 0 && ny < rows && !visited[ny][nx]) {
                // Remove wall between current cell and neighbor
                // Current cell grid coords: (2*y+1, 2*x+1)
                // Neighbor grid coords: (2*ny+1, 2*nx+1)
                // Wall coords: (y+ny+1, x+nx+1)
                
                int wallX = 2 * x + 1 + dx[i];
                int wallY = 2 * y + 1 + dy[i];
                
                maze[wallY][wallX] = ' ';

                carveMaze(nx, ny, rows, columns, visited, random);
            }
        }
    }
}
