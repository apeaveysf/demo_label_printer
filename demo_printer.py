import json
from pathlib import Path
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import Container, Vertical, Horizontal
from textual import events
from textual.widgets import Header, Footer, Static, Input, Button
from datetime import date
from zebra_labels import labels, zebra_printer

class DemoLabels(App):
    """A textual app for printing demographic labels."""

    CSS_PATH = "demo_printer.css"
    BINDINGS = [("ctrl+d", "toggle_dark", "Dark Mode"),
                ("ctrl+q", "quit", "Quit Application")]

    printer = reactive("")
    clientid = reactive("")
    name = reactive("")
    alias = reactive("")
    tests = reactive("")
    date = reactive("")
    quantity = reactive(0)

    def action_clear_fields(self, additional_skip=None):
        skip = ["field_label_printer", "field_date"]
        if additional_skip is not None:
            skip = skip + additional_skip
        for widget in self.query("Input"):
            if widget.id in skip:
                pass
            else:
                widget.value = ""
        self.set_focus(self.query_one("#field_client_id"))
    
    def action_load_client(self):
        """Load specified client into App"""
        with open(Path.cwd() / "clients.json", "r") as read_clients:
            clients = json.load(read_clients)
        if self.clientid in clients:
            self.query_one("#field_client_name").value = clients[self.clientid]["name"]
            self.query_one("#field_alias").value = clients[self.clientid]["alias"]
            self.query_one("#field_tests").value = clients[self.clientid]["order codes"]
            self.set_focus(self.query_one("#field_date"))
        else:
            self.action_clear_fields(additional_skip=["field_client_id"])
            self.set_focus(self.query_one("#field_client_name"))

    def action_print_label(self) -> None:
        """Print labels for the given criteria."""
        # print labels if Input fields are valid and complete
        with open(Path.cwd() / "printers.json", "r") as read_printers:
            printers = json.load(read_printers)
        error_message = self.query_one("#invalid_data")
        if (self.printer in printers and 
            len(self.clientid) > 0 and
            len(self.name) > 3 and
            len(self.tests) > 2 and
            len(self.date) > 5 and
            len(self.quantity) > 0 and self.quantity.isnumeric()):
            
            error_message.styles.visibility = 'hidden'
            label = labels.demo_label(self.clientid, self.name, self.tests, self.date)
            zebra_printer.print_label(label, printers[self.printer], quantity=int(self.quantity))
            self.action_clear_fields()
        else:
            error_message.styles.visibility = 'visible'

    def action_save_client(self) -> None:
        with open(Path.cwd() / "clients.json", "r") as read_clients:
            clients = json.load(read_clients)
        if (len(self.clientid) > 0 and
            len(self.name) > 3 and
            len(self.tests) > 2):
            
            if self.clientid not in clients:
                clients[self.clientid] = {}
            clients[self.clientid]["name"] = self.name
            clients[self.clientid]["order codes"] = self.tests
            clients[self.clientid]["alias"] = self.alias
            with open(Path.cwd() / "clients.json", 'w') as write_clients:
                json.dump(clients, write_clients, indent=4)

    def on_mount(self):
        """Set default start values on App start."""
        self.title = "Demographics Label Printer"
        self.query_one('#invalid_data').styles.visibility = 'hidden'
        self.set_focus(self.query_one("#field_label_printer"))

    def on_key(self, event: events.Enter) -> None:
        """Event handler for key presses."""

        # When pressing the enter key in an Input field, intelligently move to the relevant next field or button.
        if event.key == "enter":
            if self.focused.id == "field_label_printer":
                self.set_focus(self.query_one("#field_client_id"))
            elif self.focused.id == "field_client_id":
                self.action_load_client()
            elif self.focused.id == "field_client_name":
                self.set_focus(self.query_one("#field_alias"))
            elif self.focused.id == "field_alias":
                self.set_focus(self.query_one("#field_tests"))
            elif self.focused.id == "field_tests":
                self.set_focus(self.query_one("#field_date"))
            elif self.focused.id == "field_date":
                self.set_focus(self.query_one("#field_quantity"))
            elif self.focused.id == "field_quantity":
                self.action_print_label()
            elif self.focused.id == "button_reset":
                self.action_clear_fields()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update reative variables with respective field value, whenever any input value changes."""
        # event.input.id
        self.printer = self.query_one('#field_label_printer').value.upper()
        self.clientid = self.query_one("#field_client_id").value.upper()
        self.name = self.query_one("#field_client_name").value.upper()
        self.alias = self.query_one("#field_alias").value.upper()
        self.tests = self.query_one("#field_tests").value.upper()
        self.date = self.query_one("#field_date").value
        self.quantity = self.query_one("#field_quantity").value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler for button presses."""
        if event.button.id == "button_reset":
            self.action_clear_fields()
        elif event.button.id == "button_load":
            self.action_load_client()
        elif event.button.id == "button_save":
            self.action_save_client()
        else:
            # print labels if Input fields are valid and complete
            self.action_print_label()

    def compose(self) -> ComposeResult:
        """Create child widgets for app."""
        yield Header()
        yield Footer()
        yield Container(
            Horizontal(
                Static("Label Printer:", id="label_label_printer"),
                Input("LABREQ5", placeholder="<Label Printer [LABREQ/LABREQ2/etc]>", id="field_label_printer"),
                id="row1"
            ),
            Horizontal(
                Horizontal(
                    Static("Client ID:", id="label_client_id"),
                    Input(placeholder="<Client ID>", id="field_client_id"),
                    Button("Load Client", id="button_load"),
                    Button("Save/Update", id="button_save"),
                    id="span_client_id"
                ),
                id="row2"
            ),
            Horizontal(
                Horizontal(
                    Static("Name:", id="label_client_name"),
                    Input(placeholder="<Physician Name>", id="field_client_name"),
                    id="span_client_name"
                ),
                Horizontal(
                    Static("Alias:", id="label_alias"),
                    Input(placeholder="<Alias or Clinic Name>", id="field_alias"),
                    id="span_alias"
                ),
                id="row3"
            ),
            Horizontal(
                Horizontal(
                    Static("Tests:", id="label_tests"),
                    Input(placeholder="<Test Codes>", id="field_tests"),
                    id="span_tests"
                    
                ),
                Horizontal(
                    Static("Date:", id="label_date"),
                    Input(date.today().strftime("%m/%d/%Y"), placeholder="<MM/DD/YYYY>", id="field_date"),
                    id="span_date"
                ),
                Horizontal(
                    Static("Quantity:", id="label_quantity"),
                    Input(placeholder="<Quantity>", id="field_quantity"),
                    id="span_quantity"
                ),
                id="row4"
            ),
            Horizontal(
                Horizontal(
                    Static("Error: Invalid Data Entered", id="invalid_data"),
                    Button("Print", variant='success', id="button_print"),
                    Button("Reset", variant="error", id="button_reset"),
                    id="button_group_1"
                ),
                id='row5'
            )
        )



if __name__ == "__main__":
    app = DemoLabels()
    app.run()
