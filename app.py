"""Punto de entrada de la aplicación Tribuna Global IA."""

import streamlit as st


def main() -> None:
    """Configura la página inicial de la aplicación."""
    st.set_page_config(
        page_title="Tribuna Global IA",
        page_icon="⚽",
        layout="wide",
    )
    st.title("Tribuna Global IA")
    st.caption("Cada opinión juega su partido.")
    st.info("La experiencia conversacional se construirá en la actividad 2.")


if __name__ == "__main__":
    main()
