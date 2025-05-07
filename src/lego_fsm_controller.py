# src/fsm_controller.py

class UIState:
    START = "start"
    SCAN = "scan"
    CHOOSE = "choose"
    ASSEMBLY = "assembly"
    FINISH = "finish"

class FSM:
    def __init__(self):
        self.state = UIState.START
        self.step_index = 0
        self.selected_set = None

    def transition(self, new_state):
        print(f"🔄 Estado cambiado: {self.state} ➔ {new_state}")
        self.state = new_state
        if new_state == UIState.START:
            self.reset()

    def reset(self):
        self.step_index = 0
        self.selected_set = None

    def handle_input(self, input_action):
        """
        input_action: string - nombre del botón pulsado o acción detectada
        """
        if self.state == UIState.START:
            if input_action == "SCAN":
                self.transition(UIState.SCAN)

        elif self.state == UIState.SCAN:
            # Simula que el escaneo termina y detecta piezas
            self.transition(UIState.CHOOSE)

        elif self.state == UIState.CHOOSE:
            if input_action.startswith("SET"):
                self.selected_set = input_action
                self.step_index = 0
                self.transition(UIState.ASSEMBLY)

        elif self.state == UIState.ASSEMBLY:
            if input_action == "NEXT":
                self.step_index += 1
                if self.step_index >= self.get_total_steps():
                    self.transition(UIState.FINISH)
            elif input_action == "BACK":
                self.step_index = max(0, self.step_index - 1)

        elif self.state == UIState.FINISH:
            if input_action == "RETRY":
                self.transition(UIState.START)

    def get_total_steps(self):
        # Simular cantidad de pasos (puede variar según el set)
        return 5

# --- Ejemplo de uso ---

if __name__ == "__main__":
    fsm = FSM()
    fsm.handle_input("SCAN")
    fsm.handle_input("SET 2")
    fsm.handle_input("NEXT")
    fsm.handle_input("NEXT")
    fsm.handle_input("NEXT")
    fsm.handle_input("NEXT")
    fsm.handle_input("NEXT")  # último paso → FINISH
    fsm.handle_input("RETRY")
