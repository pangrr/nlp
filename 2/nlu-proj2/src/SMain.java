import org.yaml.snakeyaml.Yaml;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.List;

/**
 * Created by Omid on 3/26/2015.
 */
public class SMain {
    public static void main(String[] args) throws FileNotFoundException {
        Yaml yaml = new Yaml();
        Object data = yaml.load(new FileReader("lexicon.yaml"));
        List<YLexicalItem> list = (List<YLexicalItem>) data;
        System.out.println(list.size());
    }
}
