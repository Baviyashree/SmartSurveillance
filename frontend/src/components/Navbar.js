import React from "react";
import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="logo">Smart Surveillance</div>
      <ul className="nav-links">
        <li><a href="#home">Home</a></li>
        <li><a href="#location">Location</a></li>
        <li><a href="#alerts">Alerts</a></li>
        <li><a href="#logout" className="logout-btn">Logout</a></li>
      </ul>
    </nav>
  );
}

export default Navbar;
