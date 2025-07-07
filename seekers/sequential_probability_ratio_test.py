import math


class SPRT:
    """
    Sequential Probability Ratio Test (SPRT) for a Bernoulli process.

    Tests between two simple hypotheses:
        H0: p = p0
        H1: p = p1

    Stop and decide H1 if likelihood ratio >= B
    Stop and decide H0 if likelihood ratio <= A

    Attributes:
        p0 (float): hypothesized probability under H0
        p1 (float): hypothesized probability under H1
        alpha (float): desired Type I error rate
        beta (float): desired Type II error rate
        A (float): lower threshold = beta / (1 - alpha)
        B (float): upper threshold = (1 - beta) / alpha
        llr (float): current log-likelihood ratio = log(L1 / L0)
        n (int): number of observations processed
    """

    def __init__(self, p0, p1, alpha=0.05, beta=0.05):
        if not 0 < p0 < 1 or not 0 < p1 < 1:
            raise ValueError("p0 and p1 must be in (0,1)")
        if not 0 < alpha < 1 or not 0 < beta < 1:
            raise ValueError("alpha and beta must be in (0,1)")

        self.p0 = p0
        self.p1 = p1
        self.alpha = alpha
        self.beta = beta
        # Wald thresholds
        self.A = beta / (1 - alpha)
        self.B = (1 - beta) / alpha
        self.logA = math.log(self.A)
        self.logB = math.log(self.B)
        self.llr = 0.0
        self.n = 0
        self.finished = False

    def update(self, outcome):
        """
        Update the test with a new Bernoulli outcome.

        Args:
            outcome (bool or int): True/1 for success, False/0 for failure.

        Returns:
            If no decision yet: None.
            Upon stopping: (decision, type_I_error, type_II_error)
              decision: 1 if accept H1, 0 if accept H0
              type_I_error: posterior P(H0 | data)
              type_II_error: posterior P(H1 | data)
        """
        if outcome not in (0, 1, False, True):
            raise ValueError("Outcome must be 0/1 or False/True")

        # Increment sample count
        self.n += 1

        # Compute log-likelihood contribution
        if outcome:
            self.llr += math.log(self.p1 / self.p0)
        else:
            self.llr += math.log((1 - self.p1) / (1 - self.p0))

        # Check stopping
        if self.llr <= self.logA or self.llr >= self.logB:
            if self.llr >= self.logB:
                self.finished = True
                return 1
            else:
                self.finished = True
                return 0

        # Otherwise, continue sampling
        return None

    def get_h01_probs(self):
        # Compute posterior probabilities under equal priors
        lr = math.exp(self.llr)
        post_H1 = lr / (1 + lr)
        post_H0 = 1 / (1 + lr)

        return post_H0, post_H1

    def run(self, generator):
        """
        Convenience method: Runs the SPRT until decision given a generator of outcomes.

        Args:
            generator: iterable yielding 0/1 outcomes

        Returns:
            (decision, n, type_I_error, type_II_error)
        """
        for outcome in generator:
            result = self.update(outcome)
            if result is not None:
                decision, err_I, err_II = result
                return decision, self.n, err_I, err_II
        return None, self.n, None, None
