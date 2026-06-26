export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-left">
          <p className="footer-copy">
            Copyright © {currentYear} Team <span>!BlackBox</span>
          </p>

          <p className="footer-project">
            SUST QueueStorm Investigator
          </p>

          <div className="footer-team-block">
            <p className="footer-label">Team Members</p>

            <div className="footer-team-members">
              <span>Julfikar Jim</span>
              <span className="footer-dot">•</span>
              <span>Sajjad Hossain Soykot</span>
              <span className="footer-dot">•</span>
              <span>Abu Ubaida</span>
            </div>
          </div>
        </div>

        <div className="footer-right">
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