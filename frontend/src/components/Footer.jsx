export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <p className="footer-copy">
            Copyright © {currentYear} Team <span>!BlackBox</span>
          </p>

          <p className="footer-project">
            SUST QueueStorm Investigator
          </p>
        </div>

        <div className="footer-team-block">
          <p className="footer-label">Team Members</p>
          <p className="footer-team-members">
            Julfikar Jim
            <span className="footer-dot">•</span>
            Sajjad Hossain Soykot
            <span className="footer-dot">•</span>
            Abu Ubaida
          </p>
        </div>

        <div className="footer-credit-block">
          <div className="footer-credit-row">
            <span className="footer-role">API Developer</span>
            <a
              href="https://github.com/md-julfikar"
              target="_blank"
              rel="noreferrer"
            >
              @md-julfikar
            </a>
          </div>

          <div className="footer-credit-row">
            <span className="footer-role">Front End Developed by</span>
            <a
              href="https://github.com/SajjadHossainSoykot"
              target="_blank"
              rel="noreferrer"
            >
              @SajjadHossainSoykot
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}