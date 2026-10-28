"""Inicializa PyMySQL como drop-in de MySQLdb para Django."""
import pymysql

pymysql.install_as_MySQLdb()
