const { chromium } = require('playwright');
const axeCore = require('axe-core');
const fs = require('fs');
const path = require('path');

const targetDir = path.join(__dirname, '..', 'docs');

async function runAudit() {
  if (!fs.existsSync(targetDir)) {
    console.error('The docs directory does not exist. Please build the site with "quarto render" first.');
    process.exit(1);
  }

  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // You can add more files to this array as the site grows
  const files = ['index.html', 'cv.html', 'colophon.html', '404.html'];
  const allViolations = [];
  let totalViolations = 0;

  for (const file of files) {
    const fileUrl = 'file://' + path.join(targetDir, file);
    console.log(`\nAuditing ${file}...`);
    
    try {
      await page.goto(fileUrl);
      await page.addScriptTag({ path: require.resolve('axe-core') });
      
      const results = await page.evaluate(async () => {
        return await axe.run();
      });
      
      console.log(`Found ${results.violations.length} violations in ${file}.`);
      totalViolations += results.violations.length;
      
      for (const v of results.violations) {
        allViolations.push({ file, violation: v });
        console.log(`- ${v.id}: ${v.description}`);
        console.log(`  Impact: ${v.impact}`);
        console.log(`  WCAG: ${v.tags.join(', ')}`);
        for (const node of v.nodes.slice(0, 3)) {
          console.log(`    - ${node.html.substring(0, 100)}`);
        }
      }
    } catch (err) {
      console.error(`Error auditing ${file}:`, err.message);
    }
  }

  await browser.close();

  if (totalViolations > 0) {
    console.error(`\n❌ Audit failed with ${totalViolations} total violations.`);
    process.exit(1);
  } else {
    console.log('\n✅ Accessibility audit passed with 0 violations!');
  }
}

runAudit().catch(err => {
  console.error(err);
  process.exit(1);
});
