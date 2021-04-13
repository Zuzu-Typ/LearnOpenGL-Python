# This function is found in the camera class. What we basically do is keep the y position value at 0.0 to force our
# user to stick to the ground.

[...]
# processes input received from any keyboard-like input system. Accepts input parameter in the form of camera defined ENUM (to abstract it from windowing systems)
def ProcessKeyboard(self, direction: Camera_Movement, deltaTime: float) -> None:

    velocity = self.MovementSpeed * deltaTime
    if (direction == Camera_Movement.FORWARD):
        self.Position += self.Front * velocity
    if (direction == Camera_Movement.BACKWARD):
        self.Position -= self.Front * velocity
    if (direction == Camera_Movement.LEFT):
        self.Position -= self.Right * velocity
    if (direction == Camera_Movement.RIGHT):
        self.Position += self.Right * velocity
    # make sure the user stays at the ground level
    self.Position.y = 0.0 # <-- this one-liner keeps the user at the ground level (xz plane)

[...]

