#!/usr/bin/env python3
"""
🧮 Kalkulator Penghitung Overship v2.2
----------------------------------------
✨ Versi CLI elegan dengan Rich
✅ Siap dikonversi ke .exe (PyInstaller)
✅ Bisa digunakan berulang tanpa tutup aplikasi
"""

import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, IntPrompt

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def hitung_overship():
    clear_screen()
    console.print(Panel.fit(
        Text("🧮  KALKULATOR PENGHITUNG OVERSHIP v2.2\nby Dimas Alfredo", 
             justify="center", style="bold bright_cyan"),
        border_style="magenta"
    ))

    # Jumlah size
    console.print("[bold yellow]Masukkan jumlah size (4–8)[/bold yellow]")
    jml_size = IntPrompt.ask("Jumlah size", default=4)
    if jml_size < 1:
        console.print("[red]Jumlah size harus lebih dari 0![/red]")
        return

    # Input overship
    console.rule("[bold yellow]Input Data OVERSHIP[/bold yellow]")
    overship = []
    for i in range(1, jml_size + 1):
        qty = IntPrompt.ask(f"  Size-{i}", default=0)
        overship.append(qty)

    # Input order
    console.rule("[bold green]Input Data ORDER[/bold green]")
    order = []
    for i in range(1, jml_size + 1):
        qty = IntPrompt.ask(f"  Size-{i}", default=0)
        order.append(qty)

    # Perhitungan
    total_overship = sum(overship)
    total_order = sum(order)
    selisih_list = [overship[i] - order[i] for i in range(jml_size)]

    console.rule("[bold cyan]HASIL PERHITUNGAN[/bold cyan]")

    table = Table(title="📊 Rekapitulasi Per Size", show_lines=True, style="bold white")
    table.add_column("Size", justify="center", style="bright_blue")
    table.add_column("Overship", justify="right", style="bold yellow")
    table.add_column("Order", justify="right", style="bold green")
    table.add_column("Selisih", justify="right", style="bold cyan")

    for i in range(jml_size):
        diff = selisih_list[i]
        color = "red" if diff < 0 else "green" if diff > 0 else "white"
        diff_str = f"[{color}]{diff:+}[/]"
        table.add_row(f"Size-{i+1}", str(overship[i]), str(order[i]), diff_str)

    console.print(table)

    console.print(Panel.fit(
        f"[yellow]Total Overship:[/] [bold cyan]{total_overship}[/]\n"
        f"[green]Total Order   :[/] [bold cyan]{total_order}[/]\n"
        f"[white]Selisih Total :[/] [bold {'red' if total_overship < total_order else 'green'}]{total_overship - total_order:+}[/]",
        title="📦 Total Summary",
        border_style="bright_magenta"
    ))

def main():
    while True:
        hitung_overship()
        console.print("\n[cyan]Apa yang ingin kamu lakukan selanjutnya?[/cyan]")
        console.print("[green][1][/green] Hitung lagi   [red][2][/red] Keluar\n")
        pilihan = Prompt.ask("Pilih opsi", choices=["1", "2"], default="1")
        if pilihan == "2":
            console.print("\n[bold yellow]Terima kasih telah menggunakan Kalkulator Overship 💛[/bold yellow]")
            break

if __name__ == "__main__":
    main()
