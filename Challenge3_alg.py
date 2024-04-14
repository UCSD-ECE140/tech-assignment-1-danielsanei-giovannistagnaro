import heapq

class PriorityQueue:
    
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]
    
def manhattan_distance(a, b):
        return abs(b[0] - a[0]) + abs(b[1] - a[1])
    
def get_neighbors(node, walls):
        
        # Initialize variables
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        result = []

        # Get all neighbors
        for direction in directions:
            neighbor = (node[0] + direction[0], node[1] + direction[1])

            # Check valid neighbor
            if neighbor not in walls:  # walls = set of tuples
                result.append(neighbor)

        # Return
        return result

def a_star_search(start, goal, walls):

    # Initialize variables
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}              # dictionary maps position to previous (path reconstruction)
    cost_so_far = {}            # dictonary for cost of least expensive path so far
    came_from[start] = None
    cost_so_far[start] = 0

    # Search algorithm
    while not frontier.empty():
        current = frontier.get()

        # Check reached goal node
        if current == goal:
            break

        # Explore neighbor nodes
        for next in get_neighbors(current, walls):

            # Determine new cost
            new_cost = cost_so_far[current] + 1

            # Check if next not visited or new cost lower than previous
            if next not in cost_so_far or new_cost < cost_so_far[next]:

                # Update new cost with manhattan distance
                cost_so_far[next] = new_cost
                priority = new_cost + manhattan_distance(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

        if current != goal:
            return None, None

    # Return
    return came_from, cost_so_far

def reconstruct_path(came_from, start, goal):

    # Initialize variables
    current = goal
    path = []

    # Construct path backwards (goal -> start)
    while current != start:
        path.append(current)
        current = came_from[current]

    # Reverse to get forwards path (start -> goal)
    path.reverse()

    # Return
    return path