library(pwr)
k <- 4
n <- 200  
alpha <- 0.05
effect_sizes <- c(0.1, 0.25, 0.4)

for (f in effect_sizes) {
  power <- pwr.anova.test(k = k, n = n, f = f, sig.level = alpha)$power
  cat(sprintf("Effect size (f): %.2f, power approx (lower bound): %.3f\n", f, power))
}


Effect size (f): 0.10, power approx (lower bound): 0.652
Effect size (f): 0.25, power approx (lower bound): 1.000
Effect size (f): 0.40, power approx (lower bound): 1.000