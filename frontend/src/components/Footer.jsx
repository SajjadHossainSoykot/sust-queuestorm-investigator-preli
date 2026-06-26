export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <p className="footer-copy">
            Copyright © {currentYear} Team <span>!BlackBox</span>
          </p>
          <p className="footer-subtitle">
            SUST QueueStorm Investigator
          </p>
        </div>

        <div className="footer-info">
          <p>
            <strong>Team Members:</strong> Julfikar Jim, Sajjad Hossain Soykot,
            Abu Ubaida
          </p>

          <p>
            <strong>Front End Developed by:</strong> Sajjad Hossain Soykot{' '}
            <a
              href="https://github.com/SajjadHossainSoykot"
              target="_blank"
              rel="noreferrer"
            >
              @SajjadHossainSoykot
            </a>
          </p>

          <p>
            <strong>API Developer:</strong> Julfikar Jim{' '}
            <a
              href="https://github.com/md-julfikar"
              target="_blank"
              rel="noreferrer"
            >
              @md-julfikar
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}