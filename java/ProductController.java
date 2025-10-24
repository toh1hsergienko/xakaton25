package com.example.laba4.controller;

import com.example.laba4.model.Product;
import com.example.laba4.model.User;
import com.example.laba4.service.ProductService;
import com.example.laba4.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import jakarta.servlet.http.HttpSession;

@Controller
@RequestMapping("/products")
public class ProductController {
    @Autowired
    private ProductService productService;
    @Autowired
    private UserService userService;

    // Корневой путь перенаправляет на список товаров
    @GetMapping("/")
    public String redirectToProducts() {
        return "redirect:/products";
    }

    // Форма входа
    @GetMapping("/login")
    public String showLoginForm(Model model) {
        return "login";
    }

    // Обработка входа
    @PostMapping("/login")
    public String login(
            @RequestParam String username,
            @RequestParam String password,
            HttpSession session,
            RedirectAttributes redirectAttributes) {
        User user = userService.findByUsername(username);
        if (user != null && new BCryptPasswordEncoder().matches(password, user.getPasswordHash())) {
            session.setAttribute("currentUser", user);
            return "redirect:/products";
        }
        redirectAttributes.addFlashAttribute("error", "Неверное имя пользователя или пароль");
        return "redirect:/products/login";
    }

    // Список товаров
    @GetMapping
    public String listProducts(Model model, @SessionAttribute(name = "currentUser", required = false) User currentUser) {
        model.addAttribute("products", productService.getAllProducts());
        model.addAttribute("product", new Product());
        model.addAttribute("currentUser", currentUser);
        return "products";
    }

    // Добавление товара
    @PostMapping
    public String addProduct(@ModelAttribute Product product) {
        productService.saveProduct(product);
        return "redirect:/products";
    }

    // Удаление товара
    @PostMapping("/delete/{id}")
    public String deleteProduct(
            @PathVariable Long id,
            @SessionAttribute(name = "currentUser", required = false) User currentUser) {
        if (currentUser == null || !currentUser.getRole().equals("USER")) {
            return "redirect:/products/login";
        }
        productService.deleteProduct(id);
        return "redirect:/products";
    }

    // Админ-панель
    @GetMapping("/admin")
    public String adminPanel(Model model, @SessionAttribute(name = "currentUser", required = false) User currentUser) {
        if (currentUser == null || !currentUser.getRole().equals("ADMIN")) {
            return "redirect:/products/login";
        }
        model.addAttribute("users", userService.findAll());
        return "admin";
    }

    // Выход
    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/products/login";
    }
}